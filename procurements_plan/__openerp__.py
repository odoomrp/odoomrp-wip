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
    "name": "Procurements Plan",
    "version": "1.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Procurements",
    "depends": ['procurement',
                'project',
                'stock',
                'purchase',
                'sale',
                'sale_stock',
                'procurement_manager'
                ],
    "data": ['data/sequence.xml',
             'security/procurements_with_plan.xml',
             'security/ir.model.access.csv',
             'views/procurement_view.xml',
             'views/purchase_order_view.xml',
             'views/procurement_plan_view.xml',
             ],
    "installable": True
}
