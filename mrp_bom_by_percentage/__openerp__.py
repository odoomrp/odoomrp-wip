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
    "name": "MRP Bom By Percentage",
    "version": "1.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "MRP",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    Include in the header of the Bom list, two new fields:

        1.- Produce by percentage: Type boolean, when you check this new field,
            the quantity to be produced is 100, and the field 'amount to
            produce' will be invisible.

        2.- QTY to consume. Calculated field. Displays the sum of all amounts
            to consume.

    If the BoM list is by_percentage, will be validated that the new field
    'QTY to consume' is not greater than 100.
    """,
    "depends": ['mrp',
                ],
    "data": ['views/mrp_bom_view.xml',
             ],
    "installable": True
}
