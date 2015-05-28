# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright 2013 Camptocamp SA
#    Author: Joel Grand-Guillaume
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    "name": "Product Price History",
    "version": "1.2.3",
    "author": "Camptocamp,"
              "OdooMRP team,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "AvanzOSC",
    "category": "Generic Modules/Inventory Control",
    "depends": [
        "product",
        "product_variant_cost"
    ],
    "contributors": [
        "Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>",
        "Yannick Vaucher <yannick.vaucher@camptocamp.com>",
        "Pedro M. Baeza <pedro.baeza@serviciobaeza.com> (Migration to v8)",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "summary": "",
    "data": [
        "views/product_price_history_view.xml",
        "views/product_product_view.xml",
    ],
    "installable": True,
}
