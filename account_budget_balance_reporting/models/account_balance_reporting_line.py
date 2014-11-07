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
import openerp.addons.decimal_precision as dp
import re
from datetime import date, datetime


class AccountBalanceReportingLine(models.Model):
    """
    Account balance report line / Accounting concept
    One line of detail of the balance report representing an accounting
    concept with its values.
    The accounting concepts follow a parent-children hierarchy.
    Its values (current and previous) are calculated based on the 'value'
    formula of the linked template line.
    """

    _inherit = 'account.balance.reporting.line'

    @api.one
    @api.depends('month_start_date', 'month_end_date', 'month_report_id',
                 'template_line_id')
    def get_amounts(self):
        acc_obj = self.env['account.account']
        product_budget_obj = self.env['account.budget.product']
        account_ids = []
        amount = 0.0
        acumulated_amount = 0.0
        if (self.month_start_date and self.month_end_date and
                self.month_report_id and self.template_line_id):
            if self.template_line_id.current_value:
                tmpl_value = self.template_line_id.current_value.split(';')[0]
                for acc_code in re.findall('(-?\w*\(?[0-9a-zA-Z_]*\)?)',
                                           tmpl_value):
                    if acc_code.startswith('-'):
                        acc_code = acc_code[1:].strip()
                    if re.match(r'^debit\(.*\)$', acc_code):
                        acc_code = acc_code[6:-1]
                    elif re.match(r'^credit\(.*\)$', acc_code):
                        acc_code = acc_code[7:-1]
                    if acc_code.startswith('(') and \
                            acc_code.endswith(')'):
                        acc_code = acc_code[1:-1]
                    comp_id = self.month_report_id.company_id.id
                    account_lst = acc_obj.search([('code', '=', acc_code),
                                                  ('company_id', '=',
                                                   comp_id)])
                    for acc in account_lst:
                        child_ids = acc._get_children_and_consol()
                        account_ids.extend(child_ids)
            if account_ids:
                start_date = datetime.strptime(self.month_start_date,
                                                   '%Y-%m-%d')
                year_start_date = date(start_date.year, 1, 1)
                budget_lines = product_budget_obj.search(
                    [('account_id', 'in', account_ids),
                     ('date_start', '>=', year_start_date),
                     ('date_end', '<=', self.month_end_date)])
                for budget_line in budget_lines:
                    acumulated_amount += budget_line.expected_subtotal
                    if (budget_line.budget_line_id.date_from >=
                            self.month_start_date):
                        amount += budget_line.expected_subtotal
        self.budget_amount = amount
        self.acumulated_budget_amount = acumulated_amount

    budget_amount = fields.Float(string='Budget Amount', compute=get_amounts,
                                 digits_compute=dp.get_precision('Account'),
                                 store=True)
    acumulated_budget_amount = fields.Float(string='Acumulated Budget Amount',
                                            digits_compute=dp.get_precision(
                                                'Account'), store=True,
                                            compute=get_amounts)
