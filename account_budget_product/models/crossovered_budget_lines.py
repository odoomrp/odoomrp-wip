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
            self.env.cr.execute("""SELECT SUM(unit_amount), SUM(amount),
                AVG(amount/unit_amount) FROM account_analytic_line
                WHERE account_id=%s AND (date between
                to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                AND general_account_id=ANY(%s) AND product_id=%s""",
                       (analytic_account, date_from, date_to, acc_ids,
                        product_id))
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
    def _get_subtotal(self):
        self.expected_subtotal = self.expected_qty * self.expected_price

    product_id = fields.Many2one('product.product', string="Product")
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
    def onchange_product_id(self, cr, uid, ids, product, context=None):
        if self.product_id:
            self.expected_price = self.product_id.list_price


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

    @api.one
    def _prac(self):
        if (self.date_from and self.date_to and
                self.general_budget_id.account_ids):
            self._prac_amt()

    @api.one
    def _theo(self):
        if (self.date_from and self.date_to and
                self.general_budget_id.account_ids):
            self._theo_amt()

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

    product_budget_ids = fields.One2many('product.budget.line',
                                         'budget_line_id', copy=True,
                                         string='Product budget lines')
    partner_id = fields.Many2one("res.partner", string="Partner",
                                 related="analytic_account_id.partner_id",
                                 store=True)
    is_trimestral = fields.Boolean(string="Is trimestral",
                                   compute=_is_trimestral)
    period_id = fields.Many2one('account.period', string='Periodo')
    general_amount = fields.Float(string="General Amount", compute=_get_amount,
                                  digits_compute=dp.get_precision("Account"))
    # Son campos heredados
    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False),

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

    
    def dividir_meses(self, cr, uid, ids, fecha_inicio, fecha_fin,
                      context=None):
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(fecha_inicio, date_format)
        end_date = datetime.strptime(fecha_fin, date_format)
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
        return date_array

    def dividir_trimestres(self, cr, uid, ids, context=None):
        res = []
        result = {}
        product_line_obj = self.pool['product.budget.line']
        period_obj = self.pool['account.period']
        if not context:
            context = {}
        if ids:
            self.load_product_accounts(cr, uid, ids, context=context)
            actual_id = False
            if isinstance(ids, list):
                actual_id = ids[0]
            if actual_id:
                actual_o = self.browse(cr, uid, actual_id, context=context)
                date_lst = self.dividir_meses(cr, uid, ids, actual_o.date_from,
                                              actual_o.date_to, context)
                month_count = len(date_lst)
                if date_lst:
                    first_date = date_lst.pop(0)
                    period_ids = period_obj.find(cr, uid,
                                                 first_date['start_month'],
                                                 context=context)
                    period_lst = period_obj.search(cr, uid,
                                                   [('id', 'in', period_ids),
                                                    ('special', '=', False)])
                    new_period_id = period_lst
                    if isinstance(period_lst, list):
                        new_period_id = period_lst[0]
                    write_vals = {'date_from': first_date['start_month'],
                                  'date_to': first_date['end_month'],
                                  'es_trimestral': False,
                                  'period_id': new_period_id,
                                  'planned_amount': actual_o.planned_amount /
                                  month_count,
                                  }
                    self.write(cr, uid, [actual_id], write_vals,
                               context=context)
                    res.append(actual_id)
                    if actual_o.product_budget_ids:
                        for pro_line_o in actual_o.product_budget_ids:
                            pro_line_vals = {
                                'expected_qty': pro_line_o.expected_qty /
                                month_count,
                                }
                            product_line_obj.write(cr, uid, [pro_line_o.id],
                                                   pro_line_vals,
                                                   context=context)
                    for date_o in date_lst:
                        period_ids = period_obj.find(cr, uid,
                                                     date_o['start_month'],
                                                     context=context)
                        period_lst = period_obj.search(cr, uid,
                                                       [('id', 'in',
                                                         period_ids),
                                                        ('special', '=',
                                                         False)])
                        new_period_id = period_lst
                        if isinstance(period_lst, list):
                            new_period_id = period_lst[0]
                        line_defaults = {'date_from': date_o['start_month'],
                                         'date_to': date_o['end_month'],
                                         'period_id': new_period_id,
                                         }
                        new_id = self.copy(cr, uid, actual_id, line_defaults,
                                           context=context)
                        actual = self.browse(cr, uid, actual_id,
                                             context=context)
                        for line in actual.product_budget_ids:
                            line_defaults = {'budget_line_id':new_id}
                            product_line_obj.copy(cr, uid, line.id,
                                                  line_defaults,
                                                  context=context)
                        res.append(new_id)
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

    def copiar_trimestres(self, cr, uid, ids, context=None):
        res = []
        result = {}
        period_obj = self.pool['account.period']
        product_bud_obj = self.pool["product.budget.line"]
        if not context:
            context = {}
        if ids:
            self.load_product_accounts(cr, uid, ids, context=context)
            actual_id = False
            if isinstance(ids, list):
                actual_id = ids[0]
            if actual_id:
                actual_o = self.browse(cr, uid, actual_id, context=context)
                date_lst = self.dividir_meses(cr, uid, ids, actual_o.date_from,
                                              actual_o.date_to,
                                              context=context)
                if date_lst:
                    first_date = date_lst.pop(0)
                    period_ids = period_obj.find(cr, uid,
                                                 first_date['start_month'],
                                                 context=context)
                    period_lst = period_obj.search(cr, uid,
                                                   [('id', 'in', period_ids),
                                                    ('special', '=', False)])
                    new_period_id = period_lst
                    if isinstance(period_lst, list):
                        new_period_id = period_lst[0]
                    write_vals = {'date_from': first_date['start_month'],
                                  'date_to': first_date['end_month'],
                                  'es_trimestral': False,
                                  'period_id': new_period_id,
                                  }
                    self.write(cr, uid, [actual_id], write_vals,
                               context=context)
                    res.append(actual_id)
                    for date_o in date_lst:
                        period_ids = period_obj.find(cr, uid,
                                                     date_o['start_month'],
                                                     context=context)
                        period_lst = period_obj.search(cr, uid,
                                                       [('id', 'in',
                                                         period_ids),
                                                        ('special', '=',
                                                         False)])
                        new_period_id = period_lst
                        if isinstance(period_lst, list):
                            new_period_id = period_lst[0]
                        line_defaults = {'date_from': date_o['start_month'],
                                         'date_to': date_o['end_month'],
                                         'period_id': new_period_id,
                                         }
                        new_id = self.copy(cr, uid, actual_id, line_defaults,
                                           context=context)
                        actual = self.browse(cr, uid, actual_id, context=context)
                        for line in actual.product_budget_ids:
                            line_defaults = {'budget_line_id':new_id}
                            product_bud_obj.copy(cr, uid, line.id,
                                                 line_defaults,
                                                 context=context)
                        res.append(new_id)
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
    def copy_period(self):
        res = {}
        new_lst = []
        self.load_product_accounts()
        for record in self:
            copy_defaults = {'date_to': False,
                             'date_from': False,
                             'period_id': False
                             }
            new_id = record.copy(copy_defaults)
            new_lst.append(new_id)
        res.update({'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'crossovered.budget.lines',
                    'res_id': new_lst,
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'nodestroy': True,
                    })
        return res

    @api.one
    @api.onchange("period_id", "date_from", "date_to")
    def onchange_period(self):
        period_obj = self.pool['account.period']
        period_id = False
        if not self.period_id and self.date_from and self.date_to:
                period_ids = period_obj.find(self.date_from)
                period_lst = period_obj.search([('id', 'in', period_ids),
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
            if self.general_budget_id:
                for acc in self.general_budget_id.account_ids:
                    if acc.id not in account_lst:
                        account_lst.append(acc.id)
                for prod in record.product_budget_ids:
                    acc = False
                    if prod.product_id.property_account_income:
                        prod_acc = prod.product_id.property_account_income
                        acc = prod_acc.id
                        if prod_acc.id not in account_lst:
                            account_lst.append(prod_acc.id)
                    elif prod.product_id.categ_id:
                        categ = prod.product_id.categ_id
                        if categ.property_account_income_categ:
                            categ_account = (
                                categ.property_account_income_categ.id)
                            acc = categ_account
                            if categ_account not in account_lst:
                                account_lst.append(categ_account)
                    prod.account_id = acc
                budget_vals = {'account_ids': [(6, 0, account_lst)]}
                self.general_budget_id.write(budget_vals)
