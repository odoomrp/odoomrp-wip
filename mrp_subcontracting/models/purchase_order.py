# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    mrp_operation = fields.Many2one(
        'mrp.production.workcenter.line', 'MPR Operation')
    mrp_production = fields.Many2one(
        'mrp.production', string='MRP Production', store=True,
        related="mrp_operation.production_id")

    @api.multi
    def wkf_confirm_order(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        result = super(PurchaseOrder, self).wkf_confirm_order()
        picking = False
        if self.mrp_operation:
            for move in self.mrp_operation.production_id.move_lines:
                if move.work_order.id == self.mrp_operation.id:
                    if not picking:
                        wc_line = self.mrp_operation.routing_wc_line
                        vals = {'origin': self.mrp_operation.name,
                                'picking_type_id': wc_line.picking_type_id.id,
                                'invoice_state': 'none',
                                'partner_id': self.partner_id.id,
                                'mrp_production':
                                self.mrp_operation.production_id.id}
                        picking = picking_obj.create(vals)
                        self.mrp_operation.out_picking = picking.id
                    move.picking_id = picking.id
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
