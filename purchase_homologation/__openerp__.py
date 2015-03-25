# -*- encoding: utf-8 -*-
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
    'version': '1.0',
    'category': 'Purchase Management',
    'description': """
This module restricts making purchase orders if you don't register an
homologation record. This record can be filled with:

* Supplier and product, so the purchase is allowed for that supplier and the
  concrete product.
* Supplier and product category, so the authorization extends to all the
  products of the category or its child categories for that supplier.
* Only product or product category, allowing to purchase the product or
  products within category for any supplier.
* Start and end date that restrict the homologation to that interval of time.

You can also set the permission "Bypass purchase homologation" to certain users
to not restrict the creation of the purchase order, but only warn about the
lack of the homologation.
    """,
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
