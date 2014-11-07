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
    "name": "Avanzosc Budget Fiscal Reporting",
    "version": "1.0",
    "depends": ["account_budget_product",
                "account_monthly_balance_reporting",
                ],
    "author": "AvanzOSC",
    "category": "Analytic / Financial reporting",
    "description": """
    This module adds new column in account balance reporting line.
    This column shows budget amounts sum for each line taking into \
    account code and dates.
    """,
    "init_xml": [],
    'update_xml': ["views/account_balance_reporting_line_view.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
