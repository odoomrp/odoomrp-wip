# -*- coding: utf-8 -*-
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

from openerp.osv import osv


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute the total amounts of the SO.
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            order._calc_taxes()
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal

            for tax in order.taxes:
                amount_tax += tax.amount

            res[order.id]['amount_untaxed'] = order.pricelist_id.currency_id.round(amount_untaxed)
            res[order.id]['amount_tax'] = order.pricelist_id.currency_id.round(amount_tax)
            res[order.id]['amount_total'] = amount_untaxed + amount_tax

        return res

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class SaleOrderTax(models.Model):
    _name = 'sale.order.tax'
    _table = 'sale_order_tax2'
    _order = 'sequence'

    sale_order = fields.Many2one(comodel_name='sale.order',
                                 string='Sale Order', ondelete='cascade')
    name = fields.Char(string='Tax Description', required=True)
    base = fields.Float(string='Base', digits=dp.get_precision('Account'))
    amount = fields.Float(string='Amount', digits=dp.get_precision('Account'))
    tax_code_id = fields.Many2one(comodel_name='account.tax.code',
                                  string='Tax Code')
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when displaying a list of order tax.")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    taxes = fields.One2many(comodel_name='sale.order.tax',
                            inverse_name='sale_order', string='Taxes')

    @api.multi
    def compute(self, order):
        tax_grouped = {}
        currency = order.currency_id.with_context(
            date=order.date_order or fields.Date.context_today(order))
        for line in order.order_line:
            taxes = line.tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.product_uom_qty, line.product_id,
                order.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'order': order.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'base': currency.round(tax['price_unit'] *
                                           line.product_uom_qty),
                    'sequence': tax['sequence'],
                    'base_code_id': tax['base_code_id'],
                    'tax_code_id': tax['tax_code_id'],
                }
                key = (val['tax_code_id'], val['base_code_id'])
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    # tax_grouped[key]['base_amount'] += val['base_amount']
                    # tax_grouped[key]['tax_amount'] += val['tax_amount']
        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
        return tax_grouped

    @api.multi
    def _calc_taxes(self):
        tax_model = self.env['sale.order.tax']
        for order in self:
            order.taxes.unlink()
            for tax in self.compute(order).values():
                tax_model.create({
                    'tax_code_id': tax['tax_code_id'],
                    'sale_order': tax['order'],
                    'sequence': tax['sequence'],
                    'name': tax['name'],
                    'base': tax['base'],
                    'amount': tax['amount']})
        return True

    @api.multi
    def action_wait(self):
        self._calc_taxes()
        return super(SaleOrder, self).action_wait()

    @api.multi
    def button_dummy(self):
        res = super(SaleOrder, self).button_dummy()
        self._calc_taxes()
        return res
