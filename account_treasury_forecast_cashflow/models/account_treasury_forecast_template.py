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


class AccountTreasuryForecastTemplate(models.Model):
    _inherit = 'account.treasury.forecast.template'

    receivable_line_ids = fields.One2many(
        "account.treasury.forecast.line.template", "treasury_template_id",
        string="Receivable Line", domain=[('line_type', '=', 'receivable')])
    cashflow_ids = fields.One2many(
        "account.treasury.forecast.cashflow.template", "treasury_template_id",
        string="Cash-Flow")


class AccountTreasuryForecastLineTemplate(models.Model):
    _inherit = "account.treasury.forecast.line.template"

    line_type = fields.Selection([('recurring', 'Recurring'),
                                  ('variable', 'Variable'),
                                  ('receivable', 'Receivable')])


class AccountTreasuryForecastCashflowTemplate(models.Model):
    _name = "account.treasury.forecast.cashflow.template"
    _description = "Cash-Flow Record Template"

    name = fields.Char(string="Description")
    date = fields.Date(string="Date")
    journal_id = fields.Many2one("account.journal", string="Journal")
    amount = fields.Float(string="Amount",
                          digits_compute=dp.get_precision("Account"))
    flow_type = fields.Selection([('in', 'Input'), ('out', 'Output')],
                                 string="Type")
    treasury_template_id = fields.Many2one(
        "account.treasury.forecast.template", string="Treasury Template")

    @api.one
    @api.constrains('flow_type', 'amount')
    def _check_amount(self):
        if self.flow_type == 'in' and self.amount <= 0.0:
            raise exceptions.Warning(_("Error!:: If input cash-flow, "
                                       "amount must be positive"))
        if self.flow_type == 'out' and self.amount >= 0.0:
            raise exceptions.Warning(_("Error!:: If output cash-flow, "
                                       "amount must be negative"))
