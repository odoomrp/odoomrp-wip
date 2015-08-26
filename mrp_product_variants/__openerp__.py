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
        "product_variants_no_automatic_creation",
        "mrp_production_editable_scheduled_products",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "summary": "Customized product in manufacturing",
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_view.xml",
        "views/product_attribute_view.xml",
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
