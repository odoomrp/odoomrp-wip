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


class SaleForecastLoad(models.TransientModel):

    _name = 'sale.forecast.load'

    partner_id = fields.Many2one("res.partner", string="Partner")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    sale_id = fields.Many2one("sale.order", "Sale")
    forecast_id = fields.Many2one("procurement.sale.forecast", "Forecast")
    product_categ_id = fields.Many2one("product.category", string="Category")
    product_tmpl_id = fields.Many2one("product.template", string="Template")
    product_id = fields.Many2one("product.product", string="Product")
    factor = fields.Float(string="Factor", default=1)

    @api.onchange('sale_id')
    def sale_onchange(self):
        if self.sale_id:
            self.partner_id = self.sale_id.partner_id.id
            self.date_from = self.sale_id.date_order
            self.date_to = self.sale_id.date_order

    @api.multi
    def match_sales_forecast(self, date_lst, sales, factor):
        self.ensure_one()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        res = {}
        for sale in sales:
            date_order = sale.order_id.date_order
            date = datetime.strptime(date_order,
                                     '%Y-%m-%d %H:%M:%S').strftime("%m-%d")
            for date_dict in date_lst:
                if date >= date_dict['date_from'] and date <= \
                        date_dict['date_to']:
                    forecast = date_dict['forecast'].id
                    product = sale.product_id.id
                    partner = sale.order_id.partner_id.id
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
                        sum_qty = product_dict['qty'] + sale.product_uom_qty
                        sum_subtotal = (product_dict['amount'] +
                                        sale.price_subtotal)
                        product_dict['qty'] = sum_qty * factor
                        product_dict['amount'] = sum_subtotal
                    break
        return res

    @api.multi
    def get_sale_forecast_lists(self, forecast):
        sale_line_obj = self.env['sale.order.line']
        sale_obj = self.env['sale.order']
        product_obj = self.env['product.product']
        self.ensure_one()
        date_lst = []
        line_date_from = datetime.strptime(forecast.date_from, '%Y-%m-%d')
        line_date_to = datetime.strptime(forecast.date_to, '%Y-%m-%d')
        date_lst.append({'date_from': line_date_from.strftime("%m-%d"),
                         'date_to': line_date_to.strftime("%m-%d"),
                         'forecast': forecast})
        sales = []
        if self.sale_id:
            sales = self.sale_id
        else:
            sale_domain = [('date_order', '>=', self.date_from),
                           ('date_order', '<=', self.date_to)]
            if self.partner_id:
                sale_domain += [('partner_id', '=', self.partner_id.id)]
            sales = sale_obj.search(sale_domain)
        sale_line_domain = [('order_id', 'in', sales.ids)]
        if self.product_id:
            sale_line_domain += [('product_id', '=', self.product_id.id)]
        elif self.product_tmpl_id:
            sale_line_domain += [('product_tmpl_id', '=',
                                  self.product_tmpl_id.id)]
        elif self.product_categ_id:
            products = product_obj.search([('categ_id', '=',
                                            self.product_categ_id.id)])
            sale_line_domain += [('product_id', 'in', products.ids)]
        sale_lines = sale_line_obj.search(sale_line_domain)
        return date_lst, sale_lines

    @api.multi
    def load_sales(self):
        self.ensure_one()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        forecast = self.forecast_id
        date_lst, sale_lines = self.get_sale_forecast_lists(forecast)
        result = self.match_sales_forecast(date_lst, sale_lines, self.factor)
        for forecast in result.keys():
            for partner in result[forecast].keys():
                for product in result[forecast][partner].keys():
                    prod_vals = result[forecast][partner][product]
                    forecast_line_vals = {'product_id': product,
                                          'forecast_id': forecast,
                                          'partner_id': partner,
                                          'qty': prod_vals['qty'],
                                          'unit_price': (prod_vals['amount'] /
                                                         prod_vals['qty'])
                                          }
                    forecast_line_obj.create(forecast_line_vals)
        return True
