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
    "name": "MRP Final Product Lot",
    "version": "1.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "MRP",
    "website": "http://www.odoomrp.com",
    "description": """
    This module automatically creates the lot to the final product of the
    production order.

    In the MRP production object, two new fields are added: Manual Production
    Lot of type char, and Concatenate Lots Components of type boolean.

    The lot code is generated:

    1.- If the new field Manual Production lot has value: This data, if not the
        order number.
    2.- If the check Concatenate Lots Components, this clicked, to the previous
        point code is concatenated all lot numbers of all components used to
        make the final product.
    """,
    "depends": ['stock',
                'mrp',
                ],
    "data": ['views/mrp_production_view.xml',
             ],
    "installable": True
}
