# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    prod_parent_lot = fields.Many2one('stock.production.lot',
                                      'Parent production lot')
    picking_partner = fields.Many2one(
        'res.partner', string='Picking Partner', store=True,
        related='picking_id.partner_id')
    final_product = fields.Many2one(
        'product.product', string='Final Product', store=True,
        related='production_id.product_id')

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
