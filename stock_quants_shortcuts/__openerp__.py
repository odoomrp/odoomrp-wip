
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
    "name": "Stock Quants Shortcut",
    "version": "1.0",
    "depends": ["base", "stock", "purchase", "mrp"],
    "author": "OdooMRP team",
    "contributors": ["Mikel Arregi <mikelarregi@avanzosc.es>"],
    "category": "quants",
    "description": """
    Adds shorcut buttons to quants on manufacturing orders and purchase order.
    """,
    'data': ['views/purchase_order_view.xml',
             'views/mrp_production_view.xml'
             ],
    "installable": True,
    "auto_install": False,
}
