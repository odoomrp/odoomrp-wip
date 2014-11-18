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
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class AccountBudgetProduct(models.Model):

    _name = 'account.budget.product'

    @api.one
    def _prac_amt(self):
        budget_line = self.budget_line_id
        acc_ids = [x.id for x in budget_line.general_budget_id.account_ids]
        date_to = budget_line.date_to
        date_from = budget_line.date_from
        analytic_account = budget_line.analytic_account_id.id
        product_id = self.product_id.id
        if analytic_account:
            self.env.cr.execute(
                """SELECT SUM(unit_amount), SUM(amount),
                AVG(amount/unit_amount) FROM account_analytic_line
                WHERE account_id=%s AND (date between
                to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                AND general_account_id=ANY(%s) AND product_id=%s""",
                (analytic_account, date_from, date_to, acc_ids, product_id))
            sql_result = self.env.cr.fetchone()
            amount = 0.0
            subtotal = 0.0
            qty = 0.0
            if sql_result[0]:
                qty = sql_result[0]
            if sql_result[1]:
                subtotal = sql_result[1]
            if sql_result[2]:
                amount = sql_result[2]
            self.real_amount = amount
            self.real_subtotal = subtotal
            self.real_qty = qty

    @api.one
    def _prac(self):
            budget_line = self.budget_line_id
            date_to = budget_line.date_to
            date_from = budget_line.date_from
            if (date_from and date_to and
                    budget_line.general_budget_id.account_ids):
                self._prac_amt()

    @api.one
    @api.depends('expected_qty', 'expected_price')
    def _get_subtotal(self):
        self.expected_subtotal = self.expected_qty * self.expected_price

    product_id = fields.Many2one('product.product', string="Product")
    product_categ_id = fields.Many2one('product.category', string="Category")
    account_id = fields.Many2one('account.account', string="Account")
    expected_qty = fields.Float(string="Expected Qty",
                                digits_compute=dp.get_precision('Product UoM'))
    expected_price = fields.Float(string="Unit price",
                                  digits_compute=dp.get_precision('Account'))
    expected_subtotal = fields.Float(
        string="Expected subtotal", compute=_get_subtotal, store=True,
        digits_compute=dp.get_precision('Account'))
    budget_line_id = fields.Many2one('crossovered.budget.lines',
                                     string="Budget Line", ondelete="cascade")
    real_amount = fields.Float(string="Real Price", compute=_prac,
                               digits_compute=dp.get_precision("Account"))
    real_qty = fields.Float(string="Real Qty", compute=_prac,
                            digits_compute=dp.get_precision('Product UoM'))
    real_subtotal = fields.Float(string="Real Subtotal", compute=_prac,
                                 digits_compute=dp.get_precision("Account"))
    categ_id = fields.Many2one("product.category", string="Product Category",
                               related="product_id.categ_id", store=True)
    prod_type = fields.Selection([('product', 'Stockable Product'),
                                  ('consu', 'Consumable'),
                                  ('service', 'Service')], store=True,
                                 string="Product type",
                                 related="product_id.type")
    date_start = fields.Date(string="Date Start", store=True,
                             related="budget_line_id.date_from")
    date_end = fields.Date(string="Date end", store=True,
                           related="budget_line_id.date_to")
    period_id = fields.Many2one("account.period", string="Period", store=True,
                                related="budget_line_id.period_id")
    analytic_account = fields.Many2one(
        'account.analytic.account', string="Analytic Account", store=True,
        related="budget_line_id.analytic_account_id")
    partner_id = fields.Many2one(
        "res.partner", string="Partner", store=True,
        related="budget_line_id.analytic_account_id.partner_id")
    crossovered_budget_id = fields.Many2one(
        "crossovered.budget", string="Budget", store=True,
        related="budget_line_id.crossovered_budget_id")

    @api.one
    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.expected_price = self.product_id.list_price

    @api.multi
    def request_procurement(self):
        self.ensure_one()
        value_dict = {'product_id': self.product_id.id,
                      'uom_id': self.product_id.uom_id.id,
                      'date_planned': datetime.today(),
                      'qty': self.expected_qty,
                      'warehouse_id': self.budget_line_id.warehouse_id.id
                      }
        res_id = self.env['make.procurement'].create(value_dict)
        return {'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'make.procurement',
                'res_id': res_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


class CrossoveredBudgetLines(models.Model):

    _inherit = 'crossovered.budget.lines'

    @api.one
    def _get_amount(self):
        if self.product_budget_ids:
            kont = 0.0
            for product_line in self.product_budget_ids:
                kont += (product_line.expected_qty *
                         product_line.expected_price)
            self.general_amount = kont

    @api.multi
    def _prac_amt(self):
        result = {}
        for record in self:
            value = 0.0
            if (record.date_from and record.date_to and
                    record.general_budget_id.account_ids):
                result = super(CrossoveredBudgetLines, record)._prac_amt()
                value = result[record.id]
            result[self.id] = value
        return result

    @api.one
    def _is_trimestral(self):
        res = False
        date_format = "%Y-%m-%d"
        if (self.date_from and self.date_to):
            line_start_date = datetime.strptime(self.date_from, date_format)
            line_end_date = datetime.strptime(self.date_to, date_format)
            line_date_diff = line_end_date.month - line_start_date.month
            if line_date_diff > 0:
                res = True
        self.is_trimestral = res

    product_budget_ids = fields.One2many('account.budget.product',
                                         'budget_line_id', copy=True,
                                         string='Product budget lines')
    partner_id = fields.Many2one("res.partner", string="Partner",
                                 related="analytic_account_id.partner_id",
                                 store=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    is_trimestral = fields.Boolean(string="Is trimestral",
                                   compute=_is_trimestral)
    period_id = fields.Many2one('account.period', string='Periodo')
    general_amount = fields.Float(string="General Amount", compute=_get_amount,
                                  digits_compute=dp.get_precision("Account"))
    # Son campos heredados
    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)

    _sql_constraints = [('date_range_uniq',
                         'unique(crossovered_budget_id, date_from, date_to)',
                         'Can not match the lines on the same date range!')
                        ]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = ''
            if record.crossovered_budget_id:
                name = self.crossovered_budget_id.name
            if record.analytic_account_id:
                if record.crossovered_budget_id:
                    name = name + ' - ' + record.analytic_account_id.name
                else:
                    name = record.analytic_account_id.name
            res.append((record.id, name))
        return res

    @api.multi
    def dividir_meses(self):
        date_format = '%Y-%m-%d'
        date_list = {}
        for record in self:
            start_date = datetime.strptime(record.date_from, date_format)
            end_date = datetime.strptime(record.date_to, date_format)
            date_array = []
            date_diff = end_date.month - start_date.month
            while date_diff >= 0:
                date_dict = {}
                today = start_date + relativedelta(months=date_diff)
                initial_date = datetime(today.year, today.month, 1)
                pre_final_date = initial_date + relativedelta(months=1)
                final_date = pre_final_date + relativedelta(days=-1)
                str_initial_date = datetime.strftime(initial_date, date_format)
                str_final_date = datetime.strftime(final_date, date_format)
                date_dict.update({'start_month': str_initial_date,
                                  'end_month': str_final_date})
                date_array.append(date_dict)
                date_diff -= 1
            date_array.reverse()
            date_list[record.id] = date_array
        return date_list

    @api.multi
    def dividir_trimestres(self):
        res = []
        result = {}
        period_obj = self.env['account.period']
        self.load_product_accounts()
        budget_date_lst = self.dividir_meses()
        for record in self:
            date_lst = budget_date_lst[record.id]
            month_count = len(date_lst)
            if date_lst:
                first_date = date_lst.pop(0)
                period_ids = period_obj.find(dt=first_date['start_month'])
                periods = period_obj.search([('id', 'in', period_ids.ids),
                                             ('special', '=', False)])
                write_vals = {'date_from': first_date['start_month'],
                              'date_to': first_date['end_month'],
                              'es_trimestral': False,
                              'period_id': periods[0].id,
                              'planned_amount': record.planned_amount /
                              month_count,
                              }
                record.write(write_vals)
                res.append(record.id)
                if record.product_budget_ids:
                    for pro_line_o in record.product_budget_ids:
                        pro_line_o.expected_qty = (pro_line_o.expected_qty /
                                                   month_count)
                for date_o in date_lst:
                    period_ids = period_obj.find(dt=date_o['start_month'])
                    periods = period_obj.search([('id', 'in', period_ids.ids),
                                                 ('special', '=', False)])
                    line_defaults = {'date_from': date_o['start_month'],
                                     'date_to': date_o['end_month'],
                                     'period_id': periods[0].id,
                                     }
                    new_id = record.copy()
                    new_id.write(line_defaults)
                    res.append(new_id.id)
                result.update({'view_type': 'form',
                               'view_mode': 'tree,form',
                               'res_model': 'crossovered.budget.lines',
                               'res_id': res,
                               'view_id': False,
                               'type': 'ir.actions.act_window',
                               'target': 'current',
                               'nodestroy': True,
                               })
        return result

    @api.multi
    def copiar_trimestres(self):
        res = []
        result = {}
        period_obj = self.pool['account.period']
        self.load_product_accounts()
        budget_date_lst = self.dividir_meses()
        for record in self:
            date_lst = budget_date_lst[record.id]
            if date_lst:
                first_date = date_lst.pop(0)
                period_ids = period_obj.find(dt=first_date['start_month'])
                periods = period_obj.search([('id', 'in', period_ids.ids),
                                             ('special', '=', False)])
                write_vals = {'date_from': first_date['start_month'],
                              'date_to': first_date['end_month'],
                              'es_trimestral': False,
                              'period_id': periods[0].id,
                              }
                record.write(write_vals)
                res.append(record.id)
                for date_o in date_lst:
                    period_ids = period_obj.find(dt=date_o['start_month'])
                    period_lst = period_obj.search([('id', 'in',
                                                     period_ids.ids),
                                                    ('special', '=', False)])
                    new_period_id = period_lst
                    if isinstance(period_lst, list):
                        new_period_id = period_lst[0]
                    line_defaults = {'date_from': date_o['start_month'],
                                     'date_to': date_o['end_month'],
                                     'period_id': new_period_id.id,
                                     }
                    new_id = record.copy()
                    new_id.write(line_defaults)
                    res.append(new_id.id)
                result.update({'view_type': 'form',
                               'view_mode': 'tree,form',
                               'res_model': 'crossovered.budget.lines',
                               'res_id': res,
                               'view_id': False,
                               'type': 'ir.actions.act_window',
                               'target': 'current',
                               'nodestroy': True,
                               })
        return result

    @api.one
    @api.onchange("period_id", "date_from", "date_to")
    def onchange_period(self):
        period_obj = self.env['account.period']
        if not self.period_id and self.date_from and self.date_to:
                period_ids = period_obj.find(dt=self.date_from)
                period_lst = period_obj.search([('id', 'in', period_ids.ids),
                                                ('special', '=', False)])
                if period_lst:
                    period_id = period_lst[0]
        if self.period_id:
            if not self.date_to or not self.date_from:
                date_to = self.period_id.date_stop
                date_from = self.period_id.date_start
                self.date_to = date_to
                self.date_from = date_from
                self.period_id = period_id

    @api.multi
    def load_product_accounts(self):
        for record in self:
            account_lst = []
            if record.general_budget_id:
                account_lst += record.general_budget_id.account_ids.ids
                for prod in record.product_budget_ids:
                    acc = False
                    if prod.product_id:
                        product = prod.product_id
                        if product.property_account_income:
                            acc = prod.product_id.property_account_income
                            if acc.id not in account_lst:
                                account_lst.append(acc.id)
                        elif product.categ_id.property_account_income_categ:
                            categ = product.categ_id
                            acc = categ.property_account_income_categ
                            if acc.id not in account_lst:
                                account_lst.append(acc.id)
                    elif prod.product_categ_id.property_account_income_categ:
                        categ = prod.product_categ_id
                        acc = categ.property_account_income_categ
                        if acc.id not in account_lst:
                            account_lst.append(acc.id)
                    prod.account_id = acc
                budget_vals = {'account_ids': [(6, 0, account_lst)]}
                record.general_budget_id.write(budget_vals)

    @api.multi
    def create_procurements(self):
        procurement_obj = self.env['procurement.order']
        procure_lst = []
        for record in self:
            for product_line in record.product_budget_ids:
                if product_line.product_id:
                    procure_id = procurement_obj.create({
                        'name': ('MPS: ' + record.crossovered_budget_id.name +
                                 ' (' + record.date_from + '.' + record.date_to
                                 + ') ' + record.warehouse_id.name),
                        'date_planned': datetime.today(),
                        'product_id': product_line.product_id.id,
                        'product_qty': product_line.expected_qty,
                        'product_uom': product_line.product_id.uom_id.id,
                        'location_id': record.warehouse_id.lot_stock_id.id,
                        'company_id': record.warehouse_id.company_id.id,
                        'warehouse_id': record.warehouse_id.id,
                    })
                    procure_id.signal_workflow('button_confirm')
                    procure_lst.append(procure_id.id)
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_id': procure_lst,
            'type': 'ir.actions.act_window',
            }
