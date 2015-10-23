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
    "name": "Pricelist Rules - Purchase extension",
    "version": "1.0",
    "depends": [
        "purchase",
        "account",
        "purchase_discount",
        "product",
        "product_pricelist_rules",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "license": "AGPL-3",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Hidden/Dependency",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "data": [
        "views/purchase_pricelist_view.xml",
        "views/purchase_view.xml",
        "views/pricelist_view.xml",
        "security/ir.model.access.csv",
        "security/purchase_pricelist_rules_security.xml",
    ],
    "installable": True,
    "auto_install": True,
}
