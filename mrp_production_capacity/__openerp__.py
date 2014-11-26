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
    "name": "MRP Production Capacity",
    "version": "1.0",
    "author": "OdooMRP team",
    "contributors": [
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        ],
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- In route operations add a flag 'Limited Production Capacity', of type
        boolean.

    2.- In the OF, selecting route, assigned as default amount to manufacture
        the capacity per cycle of the machine is assigned default this
        operation routing.

    3.- If the user switches to hand the quantity to be produced, verify that
        it is between the minimum and maximum machine default the same
        operation, and if not ... give a warning.

    4.- IN OT (WorkOrder) put a onchange on the machine, changing verify
        whether the amount of the OF is between the capabilities of the new
        machine assigned in it, if not ... give notice that they have to change
        the amount in the OF.
    """,
    "depends": ['mrp',
                ],
    "data": ['views/mrp_view.xml',
             ],
    "installable": True
}
