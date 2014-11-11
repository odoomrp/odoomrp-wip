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
    "name": "MRP Procurements Plan",
    "version": "1.0",
    'author': 'OdooMRP team',
    "category": "Manufacturing",
    'website': "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- Inherit the module 'procurements_plan'.
    2.- In mrp.production object, has added a new field: Plan.

    When procurements run from the plan, all Procurements, purchases, and
    generated MRP Productions, be associated with the plan.

    """,
    "depends": ['procurements_plan',
                'mrp',
                ],
    "data": ['views/mrp_production_view.xml',
             'views/procurement_plan_view.xml',
             ],
    "installable": True
}
