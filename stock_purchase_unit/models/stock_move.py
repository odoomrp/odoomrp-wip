# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_uop_qty = fields.Float(
        string='Quantity (UoP)', states={'done': [('readonly', True)]},
        digits=dp.get_precision('Product Unit of Measure'))
    product_uop = fields.Many2one(
        comodel_name='product.uom', string='Product UoP',
        states={'done': [('readonly', True)]})

    @api.one
    @api.onchange('product_uop_qty')
    def onchange_uop_qty(self):
        if self.product_id:
            self.product_uom_qty = (self.product_uop_qty /
                                    self.product_id.uop_coeff)

    @api.multi
    def onchange_quantity(
            self, product_id, product_qty, product_uom, product_uos):
        res = super(StockMove, self).onchange_quantity(
            product_id, product_qty, product_uom, product_uos)
        if 'value' in res and self.product_id:
            res['value'].update({
                'product_uop_qty': product_qty * self.product_id.uop_coeff})
        return res
