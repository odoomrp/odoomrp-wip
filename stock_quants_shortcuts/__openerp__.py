# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
    "name": "Stock Quants Shortcuts",
    "version": "1.0",
    "depends": [
        "stock",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
    ],
    "website": "http://www.odoomrp.com",
    "category": "Warehouse Management",
    "description": """
This module will cause installing more modules:
* sale_stock_quant_shortcut if sale module is installed
* purchase_stock_quant_shortcut if purchase module is installed
* mrp_stock_quant_shortcut if mrp module is installed
    """,
    'data': [],
    "installable": True,
    "auto_install": False,
}
