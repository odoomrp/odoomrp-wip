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
    "name": "MRP Repair With Analytic",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "MRP Repair",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- Is created the new field 'Analytic Account' in the object MRP Repair.

    2.- Is created the new filed 'User' in the operations, and components of
        the repair order.

    When the repair order is confirmed, for each line of operations, and
    components, will create one analytic line.

    When the invoice is created, will take analytic account of repair, and
    takes it to the invoice line.
    """,
    "depends": ['account',
                'analytic',
                'hr_timesheet_invoice',
                'mrp_repair',
                ],
    "data": ['views/mrp_repair_view.xml',
             ],
    "installable": True
}
