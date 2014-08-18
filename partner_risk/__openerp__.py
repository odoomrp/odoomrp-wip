
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Partner Risk",
    "version": "1.0",
    "description": """
    This module adds a new button in the partner form to analyze current state
    of a partner risk.
    It reports current information regarding amount of debt in invoices,
    orders, etc.
    It also modifies the workflow of sale orders by adding a new step when
    partner's risk is exceeded.
    --Module of nan-tic nan_partner_risk ported by Factor Libre to OpenERP 7
    """,
    "author": "Factor Libre S.L, NaN·tic",
    "website": "http://www.factorlibre.com",
    "depends": ['account', 'sale_stock', 'account_payment'],
    "category": "Custom Modules",
    "data": [
        'security/partner_risk_security.xml',
#        'wizard/open_risk_window_view.xml',
        'views/risk_view.xml',
        'views/sale_view.xml',
        'views/sale_workflow.xml'],
    "active": False,
    "installable": True
}
