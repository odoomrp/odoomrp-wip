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
    'name': 'Purchase Homologation',
    'version': '1.0',
    'category': 'Purchase',
    'description': """
This module allows to homologate suppliers with certain product categories,
or even products. In purchase orders are allowed to order products from
suppliers that do not have homologated this product.
    """,
    'author': 'OdooMRP team',
    'website': 'www.odoomrp.com',
    'license': 'AGPL-3',
    'depends': ['purchase'],
    'data': ["views/purchase_homologation_view.xml"],
    'installable': True,
}
