# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta


class WizLoadSaleFromPlan(models.TransientModel):

    _name = 'wiz.load.sale.from.plan'

    def _get_default_partner(self):
        model = self.env.context.get('active_model', False)
        partner = False
        if model == 'sale.order':
            record = self.env[model].browse(self.env.context.get('active_id'))
            partner = record.partner_id
        return partner

    def _get_default_sale(self):
        model = self.env.context.get('active_model', False)
        sale = False
        if model == 'sale.order':
            record = self.env[model].browse(self.env.context.get('active_id'))
            sale = record.id
        return sale

    def _get_default_date_from(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_from = False
        if model == 'sale.order':
            date_from = record.date_order
        elif model == 'procurement.plan':
            reg_date = record.from_date
            cur_year = fields.Date.from_string(reg_date).year
            date_from = fields.Date.from_string(reg_date).replace(
                year=cur_year-1)
        return date_from

    def _get_default_date_to(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_to = False
        if model == 'sale.order':
            date_to = record.date_order
        elif model == 'procurement.plan':
            reg_date = record.to_date
            cur_year = fields.Date.from_string(reg_date).year
            date_to = fields.Date.from_string(reg_date).replace(
                year=cur_year-1)
        return date_to

    partner_id = fields.Many2one("res.partner", string="Customer",
                                 default=_get_default_partner)
    date_from = fields.Date(string="Date from", default=_get_default_date_from)
    date_to = fields.Date(string="Date to", default=_get_default_date_to)
    sale_id = fields.Many2one(
        "sale.order", "Sale", default=_get_default_sale)
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
    def load_sales(self):
        self.ensure_one()
        procurement_obj = self.env['procurement.order']
        plan = self.env['procurement.plan'].browse(
            self.env.context['active_id'])
        sale_lines = self.get_sale_lines()
        date_list = self.get_date_list(plan)
        date_start = fields.Date.from_string(self.date_from)
        date_end = fields.Date.from_string(self.date_to)
        month_count = ((date_end.year - date_start.year) * 12 +
                       date_end.month - date_start.month + 1)
        result = self.match_sales(sale_lines, self.factor)
        for date in date_list:
            for partner in result.keys():
                for product in result[partner].keys():
                    prod_vals = result[partner][product]
                    vals = self._prepare_vals_for_procurement(
                        prod_vals, plan, product, date, month_count)
                    res = procurement_obj.onchange_product_id(product)
                    if 'value' not in res:
                        prod = self.env['product.product'].browse(product)
                        raise exceptions.Warning(
                            _('Product UOM or Product UOS not found for'
                              ' product: %s') % (prod.name))
                    vals.update(res['value'])
                    proc = procurement_obj.create(vals)
                    proc.write(
                        {'rule_id': procurement_obj._find_suitable_rule(proc)})
        return True

    @api.multi
    def _prepare_vals_for_procurement(self, prod_vals, plan, product, date,
                                      month_count):
        vals = {'name': plan.name,
                'origin': plan.sequence,
                'product_id': product,
                'plan': plan.id,
                'main_project_id': plan.project_id.id,
                'product_qty': prod_vals['qty'] / month_count,
                'warehouse_id': plan.warehouse_id.id,
                'location_id':  plan.warehouse_id.lot_stock_id.id,
                'date_planned': date
                }
        return vals

    @api.multi
    def get_sale_lines(self):
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
            sale_line_domain += [
                ('product_id', 'in',
                 self.product_tmpl_id.product_variant_ids.ids)]
        elif self.product_categ_id:
            products = product_obj.search([('categ_id', '=',
                                            self.product_categ_id.id)])
            sale_line_domain += [('product_id', 'in', products.ids)]
        sale_lines = sale_line_obj.search(sale_line_domain)
        return sale_lines

    @api.multi
    def get_date_list(self, plan):
        self.ensure_one()
        date_list = []
        date_start = fields.Date.from_string(plan.from_date)
        date_end = fields.Date.from_string(plan.to_date)
        month_count = ((date_end.year - date_start.year) * 12 +
                       date_end.month - date_start.month)
        date = '-'.join([str(date_start.year), str(date_start.month), str(1)])
        first_date = fields.Date.from_string(date)
        date_list.append(date)
        while month_count > 0:
            next_date = first_date + relativedelta(months=month_count)
            date_list.append(fields.Date.to_string(next_date))
            month_count -= 1
        return date_list

    @api.multi
    def match_sales(self, sales, factor):
        self.ensure_one()
        res = {}
        for sale in sales:
            product = sale.product_id.id
            partner = self.partner_id.id
            if partner not in res:
                res[partner] = {}
            if product not in res[partner]:
                res[partner][product] = {'qty': 0.0, 'amount': 0.0}
            product_dict = res[partner][product]
            sum_qty = product_dict['qty'] + sale.product_uom_qty
            product_dict['qty'] = sum_qty * factor
        return res
