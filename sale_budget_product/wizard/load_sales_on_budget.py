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


class LoadSalesOnBudget(models.TransientModel):

    _name = 'load.sales.on.budget'

    partner_id = fields.Many2one("res.partner", string="Partner")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    sale_id = fields.Many2one("sale.order", "Sale")
    budget_id = fields.Many2one("crossovered.budget", "Budget")
    product_categ_id = fields.Many2one("product.category", string="Category")
    product_tmpl_id = fields.Many2one("product.template", string="Template")
    product_id = fields.Many2one("product.product", string="Product")

    @api.onchange('sale_id')
    def sale_onchange(self):
        if self.sale_id:
            self.partner_id = self.sale_id.partner_id.id
            self.date_from = self.sale_id.date_order
            self.date_to = self.sale_id.date_order

    @api.multi
    def match_sales_budget(self, date_lst, sales):
        self.ensure_one()
        budget_product_obj = self.env['account.budget.product']
        res = {}
        for sale in sales:
            date_order = sale.order_id.date_order
            date = datetime.strptime(date_order,
                                     '%Y-%m-%d %H:%M:%S').strftime("%m-%d")
            for date_dict in date_lst:
                if date >= date_dict['date_from'] and date <= \
                        date_dict['date_to']:
                    budget = date_dict['budget_line'].id
                    product = sale.product_id.id
                    budget_products = budget_product_obj.search(
                        [('product_id', '=', product),
                         ('budget_line_id', '=', budget)])
                    if not budget_products:
                        if budget not in res:
                            res[budget] = {}
                        if product not in res[budget]:
                            res[budget][product] = {'qty': 0.0, 'amount': 0.0}
                        sum_qty = (res[budget][product]['qty'] +
                                   sale.product_uom_qty)
                        sum_subtotal = (res[budget][product]['amount'] +
                                        sale.price_subtotal)
                        res[budget][product]['qty'] = sum_qty
                        res[budget][product]['amount'] = sum_subtotal
                    break
        return res

    @api.multi
    def get_sale_budget_lists(self, budget):
        sale_line_obj = self.env['sale.order.line']
        sale_obj = self.env['sale.order']
        product_obj = self.env['product.product']
        self.ensure_one()
        date_lst = []
        for line in budget.crossovered_budget_line:
            if line.partner_id.id == self.partner_id.id or \
                    not(line.partner_id):
                line_date_from = datetime.strptime(line.date_from, '%Y-%m-%d')
                line_date_to = datetime.strptime(line.date_to, '%Y-%m-%d')
                date_lst.append({'date_from': line_date_from.strftime("%m-%d"),
                                 'date_to': line_date_to.strftime("%m-%d"),
                                 'budget_line': line})
        sales = []
        if self.sale_id:
            sales = self.sale_id
        else:
            sale_domain = [('partner_id', '=', self.partner_id.id),
                           ('date_order', '>=', self.date_from),
                           ('date_order', '<=', self.date_to)]
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
        product_budget_obj = self.env['account.budget.product']
        budget = self.budget_id
        date_lst, sale_lines = self.get_sale_budget_lists(budget)
        result = self.match_sales_budget(date_lst, sale_lines)
        for budget_line in result.keys():
            for product in result[budget_line].keys():
                prod_vals = result[budget_line][product]
                budget_product_vals = {'product_id': product,
                                       'budget_line_id': budget_line,
                                       'expected_qty': prod_vals['qty'],
                                       'expected_price': (prod_vals['amount'] /
                                                          prod_vals['qty'])
                                       }
                product_budget_obj.create(budget_product_vals)
        return True
