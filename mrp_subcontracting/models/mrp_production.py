# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    def _created_purchases(self):
        cond = [('mrp_production', '=', self.id)]
        self.created_purchases = len(self.env['purchase.order'].search(cond))

    @api.one
    def _created_outpickings(self):
        picking_obj = self.env['stock.picking']
        cond = [('mrp_production', '=', self.id)]
        self.created_outpickings = len(
            picking_obj.search(cond).filtered(
                lambda x: x.picking_type_id.code == 'outgoing'))

    @api.one
    def _created_inpickings(self):
        picking_obj = self.env['stock.picking']
        cond = [('mrp_production', '=', self.id)]
        self.created_outpickings = len(
            picking_obj.search(cond).filtered(
                lambda x: x.picking_type_id.code == 'incoming'))

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
