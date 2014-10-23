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
    "name": "Use product supplier info for customers too (purchase extension)",
    "version": "1.0",
    "depends": [
        "purchase",
        "product_supplierinfo_for_customer",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Hidden/Dependency",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "description": """
This module extends product_supplierinfo_for_customer adding the equivalent
menu on purchase menu. It will be installed automatically if required
    """,
    "data": [],
    "installable": True,
    "auto_install": True,
}
