# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.one
    @api.depends('picking_id')
    def _get_picking_partner(self):
        self.picking_partner = False
        if self.picking_id:
            self.picking_partner = self.picking_id.partner_id.id

    @api.one
    @api.depends('production_id')
    def _get_final_product(self):
        self.final_product = False
        if self.production_id:
            self.final_product = self.production_id.product_id.id

    prod_parent_lot = fields.Many2one('stock.production.lot',
                                      'Parent production lot')
    picking_partner = fields.Many2one(
        'res.partner', string='Picking Partner', compute=_get_picking_partner,
        store=True)
    final_product = fields.Many2one(
        'product.product', string='Final Product', compute=_get_final_product,
        store=True)

    @api.multi
    def action_done(self):
        st_move_obj = self.env['stock.move']
        track_lot_obj = self.env['mrp.track.lot']
        res = super(StockMove, self).action_done()
        for final_move in self:
            if final_move.production_id:
                production_id = final_move.production_id.id
                pre_move_ids_assign = st_move_obj.search(
                    [('raw_material_production_id', '=', production_id),
                     ('state', 'not in', ('cancel', 'done'))])
                for move in pre_move_ids_assign:
                    move.prod_parent_lot = final_move.restrict_lot_id.id
                    if (move.restrict_lot_id and
                            move.raw_material_production_id):
                        production = move.raw_material_production_id
                        track_lot_obj.create(
                            {'component': move.product_id.id,
                             'component_lot': move.restrict_lot_id.id,
                             'product': production.product_id.id,
                             'product_lot': final_move.restrict_lot_id.id,
                             'production': production.id,
                             'st_move': move.id})
        return res
