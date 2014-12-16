# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    def _created_purchases(self):
        purchase_obj = self.env['purchase.order']
        cond = [('mrp_production', '=', self.id)]
        purchases = purchase_obj.search(cond)
        self.created_purchases = len(purchases)

    def _created_outpickings(self):
        picking_obj = self.env['stock.picking']
        cond = [('mrp_production', '=', self.id)]
        pickings = picking_obj.search(cond)
        cont = len([picking for picking in pickings if
                    picking.picking_type_id.code == 'outgoing'])
        self.created_outpickings = cont

    def _created_inpickings(self):
        picking_obj = self.env['stock.picking']
        cond = [('mrp_production', '=', self.id)]
        pickings = picking_obj.search(cond)
        cont = len([picking for picking in pickings if
                    picking.picking_type_id.code == 'incoming'])
        self.created_inpickings = cont

    created_purchases = fields.Integer(
        string='Created Purchases', readonly=True,
        compute='_created_purchases', track_visibility='always')
    created_outpickings = fields.Integer(
        string='Created Out Pickings', readonly=True,
        compute='_created_outpickings', track_visibility='always')
    created_inpickings = fields.Integer(
        string='Created In Pickings', readonly=True,
        compute='_created_inpickings', track_visibility='always')

    @api.one
    def action_confirm(self):
        user_obj = self.env['res.users']
        warehouse_obj = self.env['stock.warehouse']
        res = super(MrpProduction, self).action_confirm()
        user = user_obj.browse(self._uid)
        cond = [('company_id', '=', user.company_id.id)]
        warehouse = False
        for move in self.move_lines:
            if move.work_order.routing_wc_line.external:
                ptype = move.work_order.routing_wc_line.picking_type_id
                move.location_id = ptype.default_location_src_id.id
                move.location_dest_id = ptype.default_location_dest_id.id
        for wc_line in self.workcenter_lines:
            if wc_line.external:
                if not warehouse:
                    cond = [('lot_stock_id', '=', self.location_dest_id.id)]
                    warehouse = warehouse_obj.search(cond, limit=1)
                    if not warehouse:
                        raise exceptions.Warning(
                            _('Production Confirmation Error'),
                            _('Company warehouse not found'))
                wc_line.procurement_order = (
                    self._create_external_procurement(wc_line, warehouse))
        return res

    def _create_external_procurement(self, wc_line, warehouse):
        procurement_obj = self.env['procurement.order']
        vals = {'name': wc_line.name,
                'origin': wc_line.name,
                'product_id': wc_line.routing_wc_line.semifinished_id.id,
                'product_qty': self.product_qty,
                'product_uom':
                wc_line.routing_wc_line.semifinished_id.uom_id.id,
                'location_id': self.location_dest_id.id,
                'production_id': self.id,
                'warehouse_id': warehouse.id,
                'mrp_operation': wc_line.id,
                }
        procurement = procurement_obj.create(vals)
        procurement.run()
        return procurement.id


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    external = fields.Boolean(related='routing_wc_line.external', store=True,
                              readonly=True, copy=True)
    purchase_order = fields.Many2one('purchase.order', 'Purchase Order')
    out_picking = fields.Many2one('stock.picking', 'Out Picking')
    in_picking = fields.Many2one('stock.picking', 'In Picking')
    procurement_order = fields.Many2one('procurement.order',
                                        'Procurement Order')
