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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float()
    price_unit_uos = fields.Float(
        string='UoS Unit Price', readonly=True,
        digits=dp.get_precision('Product Price'),
        states={'draft': [('readonly', False)]})

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        if self.product_id:
            self.price_unit_uos = self.price_unit / self.product_id.uos_coeff

    @api.onchange('price_unit_uos')
    def onchange_price_unit_uos(self):
        if self.product_id:
            self.price_unit = self.price_unit_uos * self.product_id.uos_coeff
