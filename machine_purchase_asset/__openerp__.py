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
    'name': 'Machine Purchase Asset',
    'version': '1.0',
    'description': """
    This module links assets with machines if the created product asset is a
    machine.
    """,
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    'website': 'http://www.odoomrp.com',
    "depends": ['machine_purchase', 'account_asset'],
    "category": "Generic Modules",
    "data": ['views/machinery_view.xml',
             ],
    "installable": True,
    "auto_install": True,
}
