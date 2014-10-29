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
    "name": "MRP Wizard Filter Task",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "MRP",
    "website": "http://www.odoomrp.com",
    "description": """
    This module creates the new option menu 'Selecting tasks to impute', in
    Manufacturing.

    By selecting this new menu, a wizard will open to filter tasks by
    production order, work order, and user.
    """,
    "depends": ['mrp',
                'project',
                'mrp_project_link',
                ],
    "data": ['views/project_task_view.xml',
             'wizard/wizard_filter_mrp_task_view.xml',
             ],
    "installable": True
}
