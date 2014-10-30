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
    "name": "MRP - Product variants",
    "version": "1.0",
    "depends": [
        "product",
        "mrp",
        "mrp_operations_extension",
        "product_variants_no_automatic_creation",
        "mrp_production_editable_scheduled_products",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "description": """
Create custom product from a manufacturing order
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_view.xml",
        "views/product_view.xml",
    ],
    "installable": True,
}
