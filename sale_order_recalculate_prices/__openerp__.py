# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
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
    'name': 'Sale Order Recalculate Prices',
    'version': '1.0',
    'category': 'Sales',
    'description': """
        This module adds a button that recalculate the sale order prices.""",
    'author': 'OdooMRP team',
    'website': 'www.odoomrp.com',
    'license': 'AGPL-3',
    'depends': ['sale'],
    'data': ['views/sale_order_view.xml'],
    'installable': True,
}
