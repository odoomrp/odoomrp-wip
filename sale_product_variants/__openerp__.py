
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
    "name": "Sale - Product variants",
    "version": "1.0",
    "depends": [
        "product",
        "sale",
        "product_variants_no_automatic_creation",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Sales Management",
    "website": "http://www.odoomrp.com",
    "summary": "Product variants in sale management",
    "data": [
        "security/ir.model.access.csv",
        "security/sale_product_variants_security.xml",
        'views/res_config_view.xml',
        "views/sale_view.xml",
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
