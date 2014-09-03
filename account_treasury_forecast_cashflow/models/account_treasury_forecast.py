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

import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, exceptions, _


class AccountTreasuryForecast(models.Model):
    _inherit = "account.treasury.forecast"

    @api.one
    def calc_final_amount(self):
        super(AccountTreasuryForecast, self).calc_final_amount()
        balance = 0
        for receivable_line in self.receivable_line_ids:
            balance += receivable_line.amount
        for cashfow in self.cashflow_ids:
            balance += cashfow.amount
        self.final_amount += balance

    receivable_line_ids = fields.One2many(
        "account.treasury.forecast.line", "treasury_id",
        string="Receivable Line", domain=[('line_type', '=', 'receivable')])
    cashflow_ids = fields.One2many("account.treasury.forecast.cashflow",
                                   "treasury_id", string="Cash-Flow")

    @api.one
    def restart(self):
        res = super(AccountTreasuryForecast, self).restart()
        self.cashflow_ids.unlink()
        self.receivable_line_ids.unlink()
        return res

    @api.multi
    def button_calculate(self):
        res = super(AccountTreasuryForecast, self).button_calculate()
        self.calculate_cashflow()
        return res

    @api.one
    def calculate_cashflow(self):
        cashflow_obj = self.env['account.treasury.forecast.cashflow']
        new_cashflow_ids = []
        for cashflow_o in self.template_id.cashflow_ids:
            if ((cashflow_o.date > self.start_date and
                    cashflow_o.date < self.end_date) or
                    not cashflow_o.date):
                values = {
                    'name': cashflow_o.name,
                    'date': cashflow_o.date,
                    'template_line_id': cashflow_o.id,
                    'amount': cashflow_o.amount,
                    'flow_type': cashflow_o.flow_type,
                    'treasury_id': self.id,
                }
                new_cashflow_id = cashflow_obj.create(values)
                new_cashflow_ids.append(new_cashflow_id)
        return new_cashflow_ids


class AccountTreasuryForecastLine(models.Model):
    _inherit = "account.treasury.forecast.line"

    line_type = fields.Selection([('recurring', 'Recurring'),
                                  ('variable', 'Variable'),
                                  ('receivable', 'Receivable')])


class AccountTreasuryForecastCashflow(models.Model):
    _name = "account.treasury.forecast.cashflow"
    _description = "Cash-Flow Records"

    name = fields.Char(string="Description")
    date = fields.Date(string="Date")
    journal_id = fields.Many2one("account.journal", string="Journal")
    amount = fields.Float(string="Amount",
                          digits_compute=dp.get_precision("Account"))
    flow_type = fields.Selection([('in', 'Input'), ('out', 'Output')],
                                 string="Type")
    template_line_id = fields.Many2one(
        "account.treasury.forecast.cashflow.template",
        string="Template Line")
    treasury_id = fields.Many2one("account.treasury.forecast",
                                  string="Treasury")

    @api.one
    @api.constrains('flow_type', 'amount')
    def _check_amount(self):
        if self.flow_type == 'in' and self.amount <= 0.0:
            raise exceptions.Warning(_("Error!:: If input cash-flow, "
                                       "amount must be positive"))
        if self.flow_type == 'out' and self.amount >= 0.0:
            raise exceptions.Warning(_("Error!:: If output cash-flow, "
                                       "amount must be negative"))
