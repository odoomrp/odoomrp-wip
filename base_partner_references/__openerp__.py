# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "Partner Reference Codes",
    "version": "9.0.1.0.0",
    "license": 'AGPL-3',
    "author": 'Odoo Community Association (OCA),'
              'OdooMRP team,'
              'AvanzOSC,'
              'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    "depends": [
        "base"
    ],
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "summary": "Supplier & Customer codes",
    "description": """
    This module adds :
    * A customer reference code when the partner is supplier
    * A supplier reference code when the partner is customer

    All this data is from the partner
    """,
    "data": [
        "views/res_partner_view.xml",
    ],
    'installable': True,
    "auto_install": False,
}
