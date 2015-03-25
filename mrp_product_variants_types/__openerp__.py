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
    "name": "MRP product variants types",
    "version": "1.0",
    "depends": [
        "mrp_product_variants",
        "product_attribute_types",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Hidden/Dependency",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "description": """
This module extends product variants on MRP. It adds the possibility of
defining a custom value when the attribute is of range type.
    """,
    "data": [
        "views/mrp_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
