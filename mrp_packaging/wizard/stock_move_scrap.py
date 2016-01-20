# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class StockMoveScrap(models.TransientModel):
    _inherit = 'stock.move.scrap'

    @api.model
    def default_get(self, fields):
        res = super(StockMoveScrap, self).default_get(fields)
        move = self.env['stock.move'].browse(self.env.context.get('active_id'))
        res.update({
            'product_qty': self.env.context.get('qty_left', 0.0),
            'restrict_lot_id': move.restrict_lot_id.id or move.lot_ids[:1].id,
        })
        return res

    @api.multi
    def move_scrap(self):
        move_obj = self.env['stock.move']
        product_qty = self.product_qty
        for move_id in self.env.context.get('active_ids'):
            if product_qty > 0:
                move = move_obj.browse(move_id)
                if product_qty > move.product_uom_qty:
                    scrap = self.copy(
                        default={'product_qty': move.product_uom_qty})
                    result = super(
                        StockMoveScrap, scrap.with_context(
                            active_ids=move.ids)).move_scrap()
                    product_qty -= move.product_uom_qty
                else:
                    self.product_qty = product_qty
                    result = super(
                        StockMoveScrap, self.with_context(
                            active_ids=move.ids)).move_scrap()
        return result
