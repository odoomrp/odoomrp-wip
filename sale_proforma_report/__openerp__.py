# -*- encoding: utf-8 -*-
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
    "name": "Sale - Proforma Report",
    "version": "1.0",
    "depends": [
        "sale",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Juan Ignacio Úbeda <juanignacioubeda@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "summary": "Proforma report option in sale orders",
    "description": """
This module creates:
    * a checkbox 'proforma' on sale.order
    * Proforma header on sale order report if checkbox is clicked

    """,
    "data": [
        "views/sale_order_view.xml",
        "views/report_saleorder.xml",
    ],
    "installable": True,
}
