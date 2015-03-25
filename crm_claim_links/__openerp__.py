
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Daniel (Avanzosc) <danielcampos@avanzosc>
#    03/11/2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'CRM claim Links',
    'version': "1.0",
    'category': "Generic Modules",
    'description': """
    This module adds:

    - A link to crm claims in the stock pickings
    - A link to crm claims in repair orders
    - A Field for Supplier Stock Picking Reference in stock picking Receipts
    - For each crm claim, its associated Stock Pickings and repair orders list
    - For any product return it must have a crm claim linked.
    """,
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    'contributors': ["Daniel Campos <danielcampos@avanzosc.es>"],
    'website': "http://www.odoomrp.com",
    'depends': ["crm_claim", "mrp_repair"],
    'data': ["views/stock_picking_view.xml",
             "views/res_partner_view.xml",
             "views/mrp_repair_view.xml",
             "views/crm_claim_view.xml"
             ],
    'installable': True,
}
