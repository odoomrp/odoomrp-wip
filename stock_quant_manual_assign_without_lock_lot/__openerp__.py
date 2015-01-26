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
    "name": "Stock Quant Manual Assign Without Lock Lot",
    "version": "1.0",
    "author": "OdooMRP team",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        ],
    "category": "Stock",
    "depends": ['mrp_lock_lot',
                'stock_quant_manual_assign',
                ],
    "data": [],
    "installable": True,
    "auto_install": True,
}
