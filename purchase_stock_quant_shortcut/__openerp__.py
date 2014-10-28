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
    "name": "Purchase Stock Quant Shortcut",
    "version": "1.0",
    "depends": [
        "purchase",
        "stock",
        "stock_quants_shortcuts",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Hidden/Dependency",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "description": """
This module adds smartbutton for accessing quants from purchase orders
    """,
    "data": [
        "views/purchase_order_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
