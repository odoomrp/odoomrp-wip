# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from datetime import datetime


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    picking_ids = fields.Many2many(
        comodel_name='stock.picking', string='Pickings')

    @api.model
    def default_get(self, fields):
        item_ids = []
        packop_ids = []
        picking_ids = self.env.context.get('active_ids', [])
        for picking_id in picking_ids:
            res = super(
                StockTransferDetails,
                self.with_context(active_ids=[picking_id])).default_get(fields)
            for line in res.get('item_ids'):
                line['picking_id'] = picking_id
                item_ids.append(line)
            for line in res.get('packop_ids'):
                line['picking_id'] = picking_id
                packop_ids.append(line)
        res.update(picking_id=False, picking_ids=picking_ids,
                   item_ids=item_ids, packop_ids=packop_ids)
        return res

    @api.one
    def do_detailed_transfer(self):
        operation_obj = self.env['stock.pack.operation']
        new_pickings = []
        if len(self.picking_ids) == 1:
            result = super(StockTransferDetails, self).do_detailed_transfer()
            if self.picking_ids.wave_id:
                new_pickings = self._find_new_pickings(
                    new_pickings, self.picking_ids)
                if new_pickings:
                    self._create_new_wave(new_pickings)
            return result
        for picking in self.picking_ids:
            processed_ids = []
            # Create new and update existing pack operations
            for line in [self.item_ids.filtered(lambda x: x.picking_id.id ==
                                                picking.id),
                         self.packop_ids.filtered(lambda x: x.picking_id.id ==
                                                  picking.id)]:
                for prod in line:
                    pack_datas = {
                        'product_id': prod.product_id.id,
                        'product_uom_id': prod.product_uom_id.id,
                        'product_qty': prod.quantity,
                        'package_id': prod.package_id.id,
                        'lot_id': prod.lot_id.id,
                        'location_id': prod.sourceloc_id.id,
                        'location_dest_id': prod.destinationloc_id.id,
                        'result_package_id': prod.result_package_id.id,
                        'date': prod.date if prod.date else datetime.now(),
                        'owner_id': prod.owner_id.id,
                    }
                    if prod.packop_id:
                        prod.packop_id.write(pack_datas)
                        processed_ids.append(prod.packop_id.id)
                    else:
                        pack_datas['picking_id'] = picking.id
                        packop_id = operation_obj.create(pack_datas)
                        processed_ids.append(packop_id.id)
            # Delete the others
            cond = ['&', ('picking_id', '=', picking.id), '!',
                    ('id', 'in', processed_ids)]
            packops = operation_obj.search(cond)
            for packop in packops:
                packop.unlink()
            # Execute the transfer of the picking
            picking.do_transfer()
            new_pickings = self._find_new_pickings(new_pickings, picking)
        if new_pickings:
            self._create_new_wave(new_pickings)
        return True

    def _find_new_pickings(self, new_pickings, picking):
        picking_obj = self.env['stock.picking']
        cond = [('backorder_id', '=', picking.id)]
        new_pickings.extend(picking_obj.search(cond))
        return new_pickings

    def _create_new_wave(self, new_pickings):
        wave_obj = self.env['stock.picking.wave']
        vals = {'name': '/',
                'user_id': self._uid,
                'state': 'draft'
                }
        new_wave = wave_obj.create(vals)
        for new_picking in new_pickings:
            new_picking.write({'wave_id': new_wave.id})
        if 'origin_wave' in self._context:
            origin_wave = wave_obj.browse(self._context['origin_wave'])
            new_wave.update({'partner': origin_wave.partner})
        return new_wave


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    picking_id = fields.Many2one(
        'stock.picking', string="Picking", required=True)

    @api.one
    @api.onchange('picking_id')
    def onchange_picking(self):
        self.sourceloc_id, self.destinationloc_id = False, False
        if self.picking_id:
            self.sourceloc_id = self.picking_id.location_id
            self.destinationloc_id = self.picking_id.location_dest_id
