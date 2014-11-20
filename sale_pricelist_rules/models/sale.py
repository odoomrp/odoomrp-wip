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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class SaleOrderLineSubtotal(models.Model):
    _name = 'sale.order.line.subtotal'

    @api.one
    def _calculate_subtotal(self):
        price = (self.line_id.price_unit *
                 (1 - (self.item_id.discount or 0.0) / 100) *
                 (1 - (self.item_id.discount2 or 0.0) / 100))
        qty = self.line_id.product_uom_qty
        if self.item_id.offer_id:
            total = (self.item_id.offer_id.free_qty +
                     self.item_id.offer_id.paid_qty)
            qty = round((qty / total) * self.item_id.offer_id.paid_qty)
        taxes = self.line_id.tax_id.compute_all(
            price, qty, self.line_id.product_id, self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        self.subtotal = cur.round(taxes['total'])

    line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Line', ondelete='cascade')
    sale_id = fields.Many2one(
        comodel_name='sale.order', string='Sale Order',
        related='line_id.order_id', store=True)
    item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string='Pricelist Item',
        ondelete='cascade')
    subtotal = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        compute=_calculate_subtotal)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _calc_price_subtotal(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        return price * (1 - (self.discount2 or 0.0) / 100.0)

    def _calc_qty(self):
        qty = self.product_uom_qty
        if self.offer_id:
            total = self.offer_id.free_qty + self.offer_id.paid_qty
            qty = round((qty / total) * self.offer_id.paid_qty)
        return qty

    @api.one
    def _amount_line(self):
        new_price_subtotal = self._calc_price_subtotal()
        qty = self._calc_qty()
        taxes = self.tax_id.compute_all(
            new_price_subtotal, qty, self.product_id,
            self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        self.price_subtotal = cur.round(taxes['total'])

    discount2 = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
        readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    offer_id = fields.Many2one(
        comodel_name='product.pricelist.item.offer', string='Offer')
    item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string='Pricelist Item')
    subtotal_ids = fields.One2many(
        comodel_name='sale.order.line.subtotal', inverse_name='line_id',
        string='Subtotals by pricelist')
    price_subtotal = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        compute=_amount_line)

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         _('Second discount must be lower than 100%.')),
    ]

#     @api.model
#     def default_get(self, fields_list):
#         res = super(SaleOrderLine, self).default_get(fields_list)
#         item_obj = self.env['product.pricelist.item']
#         context = self.env.context.copy()
#         if context.get('pricelist_id'):
#             item_id = item_obj.get_best_pricelist_item(context['pricelist_id'])
#             res.update({'item_id': item_id})
#         return res

    @api.one
    @api.onchange('item_id')
    def onchange_item_id(self):
        if self.item_id:
            self.discount = self.item_id.discount
            self.discount2 = self.item_id.discount2
            self.offer_id = self.item_id.offer.id


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        tax_obj = self.pool['account.tax']
        line_obj = self.pool['sale.order.line']
        new_price_subtotal = line_obj._calc_price_subtotal(cr, uid, line)
        qty = line_obj._calc_qty(cr, uid, line)
        for c in tax_obj.compute_all(cr, uid, line.tax_id, new_price_subtotal,
                                     qty, line.product_id,
                                     line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    subtotal_ids = fields.One2many(
        comodel_name='sale.order.line.subtotal', inverse_name='sale_id',
        string='Subtotals per line by pricelist')
