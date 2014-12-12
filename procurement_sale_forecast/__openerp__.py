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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "MPS - Sale forecast",
    "version": "1.0",
    "depends": [
        "base",
        "product",
        "sale",
        "stock",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "MPS",
    "website": "http://www.odoomrp.com",
    "complexity": "normal",
    "summary": "Sale forecast",
    "description": """
This module allows to create a sale forecast
- New object to define a forecast by day, partner and products.
- New wizard to create procurements for products in forecast lines.
- New wizard on sale orders and budgets to load sale lines on budget.
    """,
    "data": [
        "views/sale_view.xml",
        "wizard/load_sales_on_forecast_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
