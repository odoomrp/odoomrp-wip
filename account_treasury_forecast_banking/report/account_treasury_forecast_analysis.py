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
from openerp import models, fields, tools


class ReportAccountTreasuryForecastAnalysis(models.Model):
    _name = "report.account.treasury.forecast.analysis"
    _description = "Treasury Forecast Analysis"
    _auto = False

    treasury_id = fields.Many2one("account.treasury.forecast",
                                  string="Treasury")
    payment_mode_id = fields.Many2one("payment.mode", string="Payment Mode")
    debit = fields.Float(string="Debit",
                         digits_compute=dp.get_precision('Account'))
    credit = fields.Float(string="Credit",
                          digits_compute=dp.get_precision('Account'))
    balance = fields.Float(string="Balance",
                           digits_compute=dp.get_precision('Account'))
    type = fields.Selection([('in', 'Input'), ('out', 'Output')],
                            string="Type")
    date = fields.Date(string="Date")

    def init(self, cr):
        tools.drop_view_if_exists(cr,
                                  'report_account_treasury_forecast_analysis')
        cr.execute("""
            create or replace view report_account_treasury_forecast_analysis
                as (
                select
                    tfl.id || 'l' AS id,
                    treasury_id,
                    tfl.date as date,
                    amount as credit,
                    0.0 as debit,
                    -amount as balance,
                    payment_mode_id,
                    'out' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_line tfl on tf.id =
                        tfl.treasury_id
                union
                select
                    tfii.id || 'i' AS id,
                    treasury_id,
                    tfii.date_due as date,
                    tfii.total_amount as credit,
                    0.0 as debit,
                    -tfii.total_amount as balance,
                    tfii.payment_mode_id,
                    'out' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_in_invoice_rel tfiir on tf.id =
                        tfiir.treasury_id inner join
                    account_treasury_forecast_invoice tfii on tfii.id =
                        tfiir.in_invoice_id
                union
                select
                    tfio.id || 'o' AS id,
                    treasury_id,
                    tfio.date_due as date,
                    0.0 as credit,
                    tfio.total_amount as debit,
                    tfio.total_amount as balance,
                    tfio.payment_mode_id,
                    'in' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_out_invoice_rel tfior on tf.id =
                        tfior.treasury_id inner join
                    account_treasury_forecast_invoice tfio on tfio.id =
                        tfior.out_invoice_id
            )""")
