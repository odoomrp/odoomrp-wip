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
    "name": "MRP Lock Lot",
    "version": "1.0",
    "author": "OdooMRP team",
    "contributors": [
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        ],
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "depends": ['stock',
                'mrp',
                ],
    "data": ['views/mrp_view.xml',
             ],
    "installable": True
}
