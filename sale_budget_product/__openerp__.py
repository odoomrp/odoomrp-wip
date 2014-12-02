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
    "name": "Sale Budget Product",
    "version": "1.0",
    "depends": ["account_budget_product",
                "sale"],
    "author": "OdooMRP team",
    "category": "",
    "description": """
        - New wizard on sale orders and budgets to load sale lines on budget.
    """,
    'data': ["wizard/load_sales_on_budget_view.xml",
             "views/crossovered_budget_view.xml",
             "views/sale_order_view.xml"],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
