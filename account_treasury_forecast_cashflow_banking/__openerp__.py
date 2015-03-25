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

{
    "name": "Account Treasury Forecast Cashflow Banking",
    "version": "1.0",
    "depends": ["account_treasury_forecast_banking",
                "account_treasury_forecast_cashflow"],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Accounting",
    "description": """
    This module:
    Sorts receivable payments and Cash-Flow records by payment mode.
    Extends Treasury Forecast Analysis Report for receivable payment and
    Cash-Flow record management.
    """,
    'data': ["views/account_treasury_forecast_template_view.xml",
             "views/account_treasury_forecast_view.xml"],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
