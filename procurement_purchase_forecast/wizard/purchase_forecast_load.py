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

from openerp import models, fields, api
from datetime import datetime


class PurchaseForecastLoad(models.TransientModel):

    _name = 'purchase.forecast.load'

    partner_id = fields.Many2one("res.partner", string="Partner")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    purchase_id = fields.Many2one("purchase.order", "Purchase")
    forecast_id = fields.Many2one("procurement.sale.forecast", "Forecast")
    product_categ_id = fields.Many2one("product.category", string="Category")
    product_tmpl_id = fields.Many2one("product.template", string="Template")
    product_id = fields.Many2one("product.product", string="Product")
    factor = fields.Float(string="Factor", default=1)

    @api.onchange('purchase_id')
    def purchase_onchange(self):
        if self.purchase_id:
            self.partner_id = self.purchase_id.partner_id.id
            self.date_from = self.purchase_id.date_order
            self.date_to = self.purchase_id.date_order

    @api.multi
    def match_purchases_forecast(self, date_lst, purchases, factor):
        self.ensure_one()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        res = {}
        for purchase in purchases:
            date_order = purchase.order_id.date_order
            date = datetime.strptime(date_order,
                                     '%Y-%m-%d %H:%M:%S').strftime("%m-%d")
            for date_dict in date_lst:
                if date >= date_dict['date_from'] and date <= \
                        date_dict['date_to']:
                    forecast = date_dict['forecast'].id
                    partner = purchase.order_id.partner_id.id
                    product = purchase.product_id.id
                    forecast_lines = forecast_line_obj.search(
                        [('product_id', '=', product),
                         ('partner_id', '=', partner),
                         ('forecast_id', '=', forecast)])
                    if not forecast_lines:
                        if forecast not in res:
                            res[forecast] = {}
                        if partner not in res[forecast]:
                            res[forecast][partner] = {}
                        if product not in res[forecast][partner]:
                            res[forecast][partner][product] = {'qty': 0.0,
                                                               'amount': 0.0}
                        product_dict = res[forecast][partner][product]
                        sum_qty = product_dict['qty'] + purchase.product_qty
                        sum_subtotal = (product_dict['amount'] +
                                        purchase.price_subtotal)
                        product_dict['qty'] = sum_qty * factor
                        product_dict['amount'] = sum_subtotal
                    break
        return res

    @api.multi
    def get_purchase_forecast_lists(self, forecast):
        purchase_line_obj = self.env['purchase.order.line']
        purchase_obj = self.env['purchase.order']
        product_obj = self.env['product.product']
        self.ensure_one()
        date_lst = []
        line_date_from = datetime.strptime(forecast.date_from, '%Y-%m-%d')
        line_date_to = datetime.strptime(forecast.date_to, '%Y-%m-%d')
        date_lst.append({'date_from': line_date_from.strftime("%m-%d"),
                         'date_to': line_date_to.strftime("%m-%d"),
                         'forecast': forecast})
        purchases = []
        if self.purchase_id:
            purchases = self.purchase_id
        else:
            purchase_domain = [('date_order', '>=', self.date_from),
                               ('date_order', '<=', self.date_to)]
            if self.partner_id:
                purchase_domain += [('partner_id', '=', self.partner_id.id)]
            purchases = purchase_obj.search(purchase_domain)
        purchase_line_domain = [('order_id', 'in', purchases.ids)]
        if self.product_id:
            purchase_line_domain += [('product_id', '=', self.product_id.id)]
        elif self.product_tmpl_id:
            purchase_line_domain += [('product_tmpl_id', '=',
                                      self.product_tmpl_id.id)]
        elif self.product_categ_id:
            products = product_obj.search([('categ_id', '=',
                                            self.product_categ_id.id)])
            purchase_line_domain += [('product_id', 'in', products.ids)]
        purchase_lines = purchase_line_obj.search(purchase_line_domain)
        return date_lst, purchase_lines

    @api.multi
    def load_purchases(self):
        self.ensure_one()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        forecast = self.forecast_id
        date_lst, purchase_lines = self.get_purchase_forecast_lists(forecast)
        result = self.match_purchases_forecast(date_lst, purchase_lines,
                                               self.factor)
        for forecast in result.keys():
            for partner in result[forecast].keys():
                for product in result[forecast][partner].keys():
                    prod_vals = result[forecast][partner][product]
                    forecast_line_vals = {'product_id': product,
                                          'forecast_id': forecast,
                                          'partner_id': partner,
                                          'qty': prod_vals['qty'],
                                          'unit_price': (prod_vals['amount'] /
                                                         prod_vals['qty']),
                                          }
                    forecast_line_obj.create(forecast_line_vals)
        return True
