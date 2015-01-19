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
from dateutil.relativedelta import relativedelta


class SaleForecastLoad(models.TransientModel):

    _name = 'sale.forecast.load'

    def _get_default_partner(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        partner = False
        if model == 'sale.order':
            partner = record.partner_id
        return partner

    def _get_default_forecast(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        forecast = False
        if model == 'procurement.sale.forecast':
            forecast = record.id
        return forecast

    def _get_default_sale(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        sale = False
        if model == 'sale.order':
            sale = record.id
        return sale

    def _get_default_date_from(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_from = False
        if model == 'sale.order':
            date_from = record.date_order
        elif model == 'procurement.sale.forecast':
            date_from = record.date_from
        return date_from

    def _get_default_date_to(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_to = False
        if model == 'sale.order':
            date_to = record.date_order
        elif model == 'procurement.sale.forecast':
            date_to = record.date_to
        return date_to

    partner_id = fields.Many2one("res.partner", string="Partner",
                                 default=_get_default_partner)
    date_from = fields.Date(string="Date from", default=_get_default_date_from)
    date_to = fields.Date(string="Date to", default=_get_default_date_to)
    sale_id = fields.Many2one("sale.order", "Sale",
                              default=_get_default_sale)
    forecast_id = fields.Many2one("procurement.sale.forecast", "Forecast",
                                  default=_get_default_forecast)
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

    @api.onchange('forecast_id')
    def forecast_onchange(self):
        if self.forecast_id:
            self.date_from = self.forecast_id.date_from
            self.date_to = self.forecast_id.date_to

    @api.multi
    def match_sales_forecast(self, sales, factor):
        self.ensure_one()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        res = {}
        for sale in sales:
            forecast = self.forecast_id.id
            product = sale.product_id.id
            partner = self.partner_id.id or False
            forecast_lines = forecast_line_obj.search(
                [('product_id', '=', product),
                 ('partner_id', '=', partner),
                 ('forecast_id', '=', forecast)])
            if not forecast_lines:
                if partner not in res:
                    res[partner] = {}
                if product not in res[partner]:
                    res[partner][product] = {'qty': 0.0, 'amount': 0.0}
                product_dict = res[partner][product]
                sum_qty = product_dict['qty'] + sale.product_uom_qty
                sum_subtotal = (product_dict['amount'] +
                                sale.price_subtotal)
                product_dict['qty'] = sum_qty * factor
                product_dict['amount'] = sum_subtotal
        return res

    @api.multi
    def get_date_list(self, forecast):
        self.ensure_one()
        date_list = []
        date_format = '%Y-%m-%d'
        date_start = datetime.strptime(forecast.date_from, date_format)
        date_end = datetime.strptime(forecast.date_to, date_format)
        month_count = ((date_end.year - date_start.year) * 12 + date_end.month
                       - date_start.month)
        first_date = datetime(date_start.year, date_start.month, 1)
        date_list.append(datetime.strftime(first_date, date_format))
        while month_count > 0:
            next_date = first_date + relativedelta(months=month_count)
            date_list.append(datetime.strftime(next_date, date_format))
            month_count -= 1
        return date_list

    @api.multi
    def get_sale_forecast_lists(self, forecast):
        sale_line_obj = self.env['sale.order.line']
        sale_obj = self.env['sale.order']
        product_obj = self.env['product.product']
        self.ensure_one()
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
        return sale_lines

    @api.multi
    def load_sales(self):
        self.ensure_one()
        date_format = '%Y-%m-%d'
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        forecast = self.forecast_id
        sale_lines = self.get_sale_forecast_lists(forecast)
        date_list = self.get_date_list(forecast)
        date_start = datetime.strptime(self.date_from, date_format)
        date_end = datetime.strptime(self.date_to, date_format)
        month_count = ((date_end.year - date_start.year) * 12 + date_end.month
                       - date_start.month + 1)
        result = self.match_sales_forecast(sale_lines, self.factor)
        for date in date_list:
            for partner in result.keys():
                for product in result[partner].keys():
                    prod_vals = result[partner][product]
                    forecast_line_vals = {'product_id': product,
                                          'forecast_id': self.forecast_id.id,
                                          'partner_id': partner,
                                          'date': date,
                                          'qty': (prod_vals['qty'] /
                                                  month_count),
                                          'unit_price': (prod_vals['amount'] /
                                                         prod_vals['qty'])
                                          }
                    forecast_line_obj.create(forecast_line_vals)
        return True
