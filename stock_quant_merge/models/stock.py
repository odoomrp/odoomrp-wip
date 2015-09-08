# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def merge_stock_quants(self):
        pending_quants = {q for q in self if not q.reservation_id and q.qty > 0}
        while pending_quants:
            quant2merge = pending_quants.pop()
            history_ids = set(quant2merge.history_ids.ids)
            # Quants must share product, lot, package, location and history
            quants = self.search(
                [('id', '!=', quant2merge.id),
                 ('product_id', '=', quant2merge.product_id.id),
                 ('lot_id', '=', quant2merge.lot_id.id),
                 ('package_id', '=', quant2merge.package_id.id),
                 ('qty', '>', 0),
                 ('location_id', '=', quant2merge.location_id.id),
                 ('reservation_id', '=', False),
                 ('propagated_from_id', '=', quant2merge.propagated_from_id.id)]
                ).filtered(lambda q: set(q.history_ids.ids) == history_ids)
            qty = quant2merge.qty + sum(q.qty for q in quants)
            value = quant2merge.qty * quant2merge.cost + sum(q.qty*q.cost for q in quants)
            cost = value / qty
            quant2merge.sudo().write({'qty': qty, 'cost': cost})
            for q in quants:
                pending_quants.discard(q)
            quants.sudo().unlink()

    @api.model
    def quants_unreserve(self, move):
        quants = move.reserved_quant_ids
        super(StockQuant, self).quants_unreserve(move)
        quants.merge_stock_quants()
