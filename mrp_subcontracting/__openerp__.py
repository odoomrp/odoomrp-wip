# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "MRP Subcontracting",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "description": """
The module implements the complete route for a subcontrating production
operations.
    """,
    "depends": [
        'mrp',
        'mrp_operations_extension',
    ],
    "data": ["views/mrp_subcontracting_view.xml",
         "views/mrp_operations_view.xml",
             ],
    "installable": True
}
