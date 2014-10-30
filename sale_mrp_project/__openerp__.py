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
    "name": "Mrp Sale Project Link",
    "version": "1.0",
    "depends": ["mrp_project_link",
                "sale",
                "stock",
                "purchase"],
    "author": "OdooMRP team",
    "category": "",
    "description": """
            This module links sales, procurements, manufacturing and purchases
            with a general project, when a product is defined as "Make to
            Order".
    """,
    'data': ["views/sale_order_view.xml",
             "views/purchase_order_view.xml",
             "views/procurement_order_view.xml",
             "views/mrp_production_view.xml",
             "views/project_project_view.xml"],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
