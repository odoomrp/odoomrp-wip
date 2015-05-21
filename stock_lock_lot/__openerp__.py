# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c)
#    2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
#    2015 AvanzOsc (http://www.avanzosc.es)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Stock Lock Lot",
    "Summary": "Restrict blocked lots in Stock Moves and reservations",
    "version": "1.0",
    "author": "OdooMRP team,"
              "Avanzosc,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        ],
    "category": "Manufacturing",
    "depends": ["stock",
                "product",
                ],
    "data": [
        "data/stock_lock_lot_data.xml",
        "wizard/stock_transfer_details_view.xml",
        "wizard/wiz_lock_lot_view.xml",
        "views/product_category_view.xml",
        "views/stock_production_lot_view.xml",
        "views/stock_quant_view.xml",
    ],
    "installable": True,
}
