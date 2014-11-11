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
    "name": "MRP Routing Workcenter",
    "version": "1.0",
    "author": "OdooMRP team",
    "contributors": [
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        ],
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- In object 'mrp.routing", create the new field Work Center.

    2.- In object 'mrp.workcenter", create the new field 'Capacity per cicle
        min'. Also puts the 'Capacity per cycle maximum.' descrition to the
        'capacity_per_cycle' field.
    3.- When the routing is selected in MRP Production, the maximum capacity
        of the cycle is put automatically into the amount to produce.

    When the quantity to be produced is changed, and this is < or > than the
    capacity per cicle, minimun or maximun, one warning of this fact is shown.
    """,
    "depends": ['mrp',
                ],
    "data": ['views/mrp_view.xml',
             ],
    "installable": True
}
