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
    "name": "Pricelist Rules - Sale extension",
    "version": "1.0",
    "depends": [
        "sale",
        "account",
        "product",
        "product_pricelist_rules",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "complexity": "normal",
    "summary": "",
    "description": """
This module allows to apply *product_pricelist_rules* extended features to
sale order lines and gets the best pricelist rule automatically.

**Warning**: This module requires *product_pricelist_rules* that is
incompatible with *product_visible_discount*
    """,
    "data": [
        "views/sale_pricelist_view.xml",
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": True,
}
