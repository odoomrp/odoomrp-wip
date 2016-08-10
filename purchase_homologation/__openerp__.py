# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

{
    'name': 'Purchase homologation',
    'version': '8.0.1.0.0',
    'category': 'Purchase Management',
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    'contributors': [
        'Carlos Sánchez Cifuentes <csanchez@grupovermon.com>',
        'Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>',
    ],
    'website': 'www.odoomrp.com',
    'license': 'AGPL-3',
    'depends': ['purchase'],
    'data': [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/purchase_homologation_view.xml",
    ],
    'installable': True,
}
