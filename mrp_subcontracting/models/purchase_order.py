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
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    mrp_operation = fields.Many2one(
        'mrp.production.workcenter.line', 'MPR Operation')
    mrp_production = fields.Many2one(
        'mrp.production', string='MRP Production', store=True,
        related="mrp_operation.production_id")

    @api.one
    def wkf_confirm_order(self):
        picking_obj = self.env['stock.picking']
        result = super(PurchaseOrder, self).wkf_confirm_order()
        picking = False
        if self.mrp_operation:
            for move in self.mrp_operation.production_id.move_lines:
                if (move.work_order.id == self.mrp_operation.id and
                        move.location_id.usage == 'internal'):
                    if not picking:
                        wc_line = self.mrp_operation.routing_wc_line
                        vals = {'origin': self.mrp_operation.name,
                                'picking_type_id': wc_line.picking_type_id.id,
                                'invoice_state': 'none',
                                'mrp_production':
                                self.mrp_operation.production_id.id
                                }
                        picking = picking_obj.create(vals)
                        vals = {'out_picking': picking.id}
                        self.mrp_operation.write(vals)
                    vals = {'picking_id': picking.id}
                    move.write(vals)
        return result

    @api.one
    def action_picking_create(self):
        picking_obj = self.env['stock.picking']
        result = super(PurchaseOrder, self).action_picking_create()
        if self.mrp_operation:
            cond = [('origin', '=', self.name)]
            picking = picking_obj.search(cond, limit=1)
            self.mrp_operation.in_picking = picking.id
            picking.mrp_production = self.mrp_operation.production_id.id
        return result
