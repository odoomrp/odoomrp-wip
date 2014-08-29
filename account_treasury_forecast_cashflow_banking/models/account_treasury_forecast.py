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


class AccountTreasuryForecastReceivable(models.Model):
    _inherit = 'account.treasury.forecast.receivable'

    payment_mode_id = fields.Many2one("payment.mode", string="Payment Mode")


class AccountTreasuryForecastCashflow(models.Model):
    _inherit = 'account.treasury.forecast.cashflow'

    payment_mode_id = fields.Many2one("payment.mode", string="Payment Mode")


class AccountTreasuryForecast(models.Model):
    _inherit = 'account.treasury.forecast'

    @api.one
    def calculate_receivable(self):
        result = super(AccountTreasuryForecast, self).calculate_receivable()
        for receivable_o in result:
            payment_mode_id = receivable_o.template_line_id.payment_mode_id.id
            receivable_o.payment_mode_id = payment_mode_id
        return result

    @api.one
    def calculate_cashflow(self, cr, uid, treasury_id, context=None):
        result = super(AccountTreasuryForecast, self).calculate_cashflow()
        for cashflow_o in result:
            payment_mode_id = cashflow_o.template_line_id.payment_mode_id.id
            cashflow_o.payment_mode_id = payment_mode_id
        return result
