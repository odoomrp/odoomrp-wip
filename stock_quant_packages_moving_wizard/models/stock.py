# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    def move_to(self, dest_location):
        last_move = self._get_latest_move(self)
        new_move = last_move.copy()
        new_move.location_id = new_move.location_dest_id
        new_move.location_dest_id = dest_location
        new_move.date_expected = fields.Datetime.now()
        new_move.date = new_move.date_expected
        new_move.product_uom_qty = self.qty
        new_move.action_done()
