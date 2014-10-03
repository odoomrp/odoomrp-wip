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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Mrp Project Link",
    "version": "1.0",
    "depends": ["mrp_operations_project"],
    "author": "Odoo MRP team",
    "category": "Manufacturing",
    "description": """
        New Manufacturing Order(MO) and Workorder(WO) links on Project Task.

        New Features:
            - When a MO starts, create a task and assign to the order.
            - When a WO starts:
                * Create a task for each user assigned to the WO.
                * Assign all created task to the WO.
                * Assign all created task to the Workorder's MO.
                * Assign MO's task as WO's task's parent.
    """,
    'data': ["views/project_task_view.xml",
             "views/mrp_production_view.xml"],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
