# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _find_moves_from_stock_planning(
        self, company, to_date, from_date=None, category=None, template=None,
        product=None, location_id=None, location_dest_id=None,
            without_reservation=False):
        reservation_obj = self.env['stock.reservation']
        moves = super(StockMove, self)._find_moves_from_stock_planning(
            company, to_date, from_date=from_date, category=category,
            template=template, product=product, location_id=location_id,
            location_dest_id=location_dest_id)
        if not without_reservation:
            return moves
        final_moves = self.env['stock.move']
        for move in moves:
            cond = [('move_id', '=', move.id)]
            reservation = reservation_obj.search(cond, limit=1)
            if not reservation:
                final_moves |= move
        return final_moves
