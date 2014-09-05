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

from openerp import models, tools


class ReportAccountTreasuryForecastAnalysis(models.Model):
    _inherit = "report.account.treasury.forecast.analysis"

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
                    CASE WHEN tfl.line_type='receivable' THEN amount
                    ELSE 0.0
                    END as credit,
                    CASE WHEN tfl.line_type='receivable' THEN 0.0
                    ELSE amount
                    END as debit,
                    CASE WHEN tfl.line_type='receivable' THEN -amount
                    ELSE amount
                    END as balance,
                    payment_mode_id,
                    'out' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_line tfl on tf.id =
                        tfl.treasury_id
                union
                select
                    tcf.id || 'c' AS id,
                    treasury_id,
                    tcf.date as date,
                    amount as credit,
                    0.0 as debit,
                    -amount as balance,
                    payment_mode_id,
                    flow_type as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_cashflow tcf on tf.id =
                        tcf.treasury_id
                union
                select
                    tfii.id || 'i' AS id,
                    treasury_id,
                    tfii.date_due as date,
                    0.0 as credit,
                    tfii.total_amount as debit,
                    tfii.total_amount as balance,
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
                    tfio.total_amount as credit,
                    0.0 as debit,
                    -tfio.total_amount as balance,
                    tfio.payment_mode_id,
                    'in' as type
                from
                    account_treasury_forecast tf inner join
                    account_treasury_forecast_out_invoice_rel tfior on tf.id =
                        tfior.treasury_id inner join
                    account_treasury_forecast_invoice tfio on tfio.id =
                        tfior.out_invoice_id
            )""")
