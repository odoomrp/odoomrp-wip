# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    purchases = fields.One2many(
        comodel_name='purchase.order', inverse_name='mrp_production',
        string='Purchases')
    created_purchases = fields.Integer(
        string='Created Purchases', readonly=True,
        compute='_compute_subcontracting_relateds', track_visibility='always')

    outpickings = fields.One2many(
        comodel_name='stock.picking', string='Out pickings', readonly=True,
        compute='_compute_subcontracting_relateds')
    created_outpickings = fields.Integer(
        string='Created Out Pickings', readonly=True,
        compute='_compute_subcontracting_relateds', track_visibility='always')

    inpickings = fields.One2many(
        comodel_name='stock.picking', string='Out pickings', readonly=True,
        compute='_compute_subcontracting_relateds')
    created_inpickings = fields.Integer(
        string='Created In Pickings', readonly=True,
        compute='_compute_subcontracting_relateds', track_visibility='always')

    @api.multi
    def _compute_subcontracting_relateds(self):
        for mo in self:
            mo.created_purchases = len(mo.purchases)
            pickings = mo.purchases.mapped('picking_ids')
            mo.outpickings = pickings.filtered(
                lambda pick: pick.picking_type_id.code == 'outgoing')
            mo.created_outpickings = len(mo.outpickings)
            mo.inpickings = pickings.filtered(
                lambda pick: pick.picking_type_id.code == 'incoming')
            mo.created_inpickings = len(mo.inpickings)

    @api.one
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for move in self.move_lines:
            if (move.work_order.routing_wc_line.external and
                    move.work_order.routing_wc_line.picking_type_id):
                ptype = move.work_order.routing_wc_line.picking_type_id
                move.location_id = ptype.default_location_src_id.id
                move.location_dest_id = ptype.default_location_dest_id.id
        for wc_line in self.workcenter_lines:
            if wc_line.external:
                wc_line.procurement_order = (
                    self._create_external_procurement(wc_line))
        return res

    @api.multi
    def action_cancel(self):
        res = super(MrpProduction, self).action_cancel()
        wc_lines = self.mapped('workcenter_lines')
        wc_external_lines = wc_lines.filtered('external')
        procurement_orders = wc_external_lines.mapped('procurement_order')
        procurement_orders.cancel()
        return res

    @api.multi
    def action_show_purchases(self):
        return {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('purchases').ids)],
            'name': 'Created Purchases',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
        }

    @api.multi
    def action_show_outpicking(self):
        return {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('outpickings').ids)],
            'name': 'Out Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
        }

    @api.multi
    def action_show_inpicking(self):
        return {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('inpickings').ids)],
            'name': 'In Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
        }

    def _prepare_extenal_procurement(self, wc_line):
        wc = wc_line.routing_wc_line
        name = "%s: %s" % (wc_line.production_id.name, wc_line.name)
        return {
            'name': name,
            'origin': name,
            'product_id': wc.semifinished_id.id,
            'product_qty': self.product_qty,
            'product_uom': wc.semifinished_id.uom_id.id,
            'location_id': self.location_dest_id.id,
            'production_id': self.id,
            'warehouse_id': wc.picking_type_id.warehouse_id.id,
            'mrp_operation': wc_line.id,
        }

    def _create_external_procurement(self, wc_line):
        procurement = self.env['procurement.order'].create(
            self._prepare_extenal_procurement(wc_line))
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
