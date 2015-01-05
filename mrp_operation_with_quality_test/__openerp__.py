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
    "name": "MRP Operation with Quality Test",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "depends": [
        'mrp',
        'mrp_operations',
        'mrp_operations_extension',
        'quality_control',
        'account',
    ],
    "data": [
        'views/mrp_routing_operation_view.xml',
        'views/mrp_production_workcenter_line_view.xml',
    ],
    "installable": True
}
