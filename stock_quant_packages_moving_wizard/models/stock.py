# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    def move_to(self, dest_location):
        move_obj = self.env['stock.move']
        new_move = move_obj.create({
            'name': 'Move %s to %s' % (self.product_id.name,
                                       dest_location.name),
            'product_id': self.product_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': dest_location.id,
            'product_uom_qty': self.qty,
            'product_uom': self.product_id.uom_id.id,
            'date_expected': fields.Datetime.now(),
            'date': fields.Datetime.now(),
            'quant_ids': [(4, self.id)],
            'restrict_lot_id': self.lot_id.id
        })
        new_move.action_done()
