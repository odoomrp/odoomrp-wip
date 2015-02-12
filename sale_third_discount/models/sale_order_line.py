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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class SaleOrderLineSubtotal(models.Model):
    _inherit = 'sale.order.line.subtotal'

    @api.one
    def _calculate_subtotal(self):
        price = (self.line_id.price_unit *
                 (1 - (self.item_id.discount or 0.0) / 100) *
                 (1 - (self.item_id.discount2 or 0.0) / 100) *
                 (1 - (self.item_id.discount3 or 0.0) / 100))
        qty = self.line_id.product_uom_qty
        if self.item_id.offer_id:
            total = (self.item_id.offer_id.free_qty +
                     self.item_id.offer_id.paid_qty)
            qty = round((qty / total) * self.item_id.offer_id.paid_qty)
        taxes = self.line_id.tax_id.compute_all(
            price, qty, self.line_id.product_id, self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        self.subtotal = cur.round(taxes['total'])

    subtotal = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        compute='_calculate_subtotal')


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def _calc_price_subtotal(self):
        self.ensure_one()
        price = super(SaleOrderLine, self)._calc_price_subtotal()
        return price * (1 - (self.discount3 or 0.0) / 100.0)

    discount3 = fields.Float(
        string='Discount 3 (%)', digits=dp.get_precision('Discount'),
        readonly=True, states={'draft': [('readonly', False)]}, default=0.0)

    _sql_constraints = [
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         _('Third discount must be lower than 100%.')),
    ]

    @api.one
    @api.onchange('item_id')
    def onchange_item_id(self):
        super(SaleOrderLine, self).onchange_item_id()
        if self.item_id:
            self.discount3 = self.item_id.discount3
