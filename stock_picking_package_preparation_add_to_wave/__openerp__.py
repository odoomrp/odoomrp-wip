# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c)
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
    'name': 'Stock picking package preparation add to wave',
    'version': "1.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    'website': "http://www.odoomrp.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com",
        "Ana Juaristi <ajuaristo@gmail.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    'category': 'Stock Management',
    'depends': ["stock_picking_package_preparation",
                "stock_picking_wave",
                ],
    'data': ["security/ir.model.access.csv",
             "wizard/wiz_picking_to_wave_view.xml",
             "views/stock_picking_package_preparation_view.xml",
             ],
    'installable': True,
}
