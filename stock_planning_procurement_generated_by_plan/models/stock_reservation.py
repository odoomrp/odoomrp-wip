# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class StockReservation(models.Model):
    _inherit = 'stock.reservation'

    def _find_reservations_from_stock_planning(
            self, company, from_date, to_date, product, location_id,
            location_dest_id):
        move_obj = self.env['stock.move']
        cond = [('company_id', '=', company.id),
                ('date', '<=', to_date),
                ('product_id', '=', product.id),
                ('location_id', '=', location_id.id),
                ('location_dest_id', '=', location_dest_id.id),
                ('state', 'not in', ('done', 'cancel'))]
        if from_date:
            cond.append(('date', '>=', from_date))
        moves = move_obj.search(cond)
        reservations = self.env['stock.reservation']
        for move in moves:
            cond = [('move_id', '=', move.id)]
            reservation = self.search(cond, limit=1)
            if reservation:
                reservations |= reservation
        return reservations
