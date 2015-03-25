
# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "Invoicing type on pickings",
    "version": "1.0",
    "depends": ["sale_journal", "stock_account"],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": ["Mikel Arregi <mikelarregi@avanzosc.es>",
                     "Ainara Galdona <ainaragaldona@avanzosc.es>"],
    "category": "stock_picking",
    "description": """
        This propagates invoicing type from sale order to stock picking.
        Wizard Create invoice from picking:
            Group by partner according to invoicing type's config.
    """,
    'data': ["wizard/stock_invoice_onshipping_view.xml"],
    "installable": True,
    "auto_install": False,
}
