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
    "name": "CRM Corrective Measures",
    "version": "1.0",
    "depends": [
        "base",
        "crm_claim",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "website": "www.odoomrp.com",
    "category": "Custom Modules",
    "description": """
        This module extends CRM Claims with corrective measures
    """,
    "data": [
        'security/ir.model.access.csv',
        'views/crm_claim_view.xml',
        'data/crm_claim_corrective_sequence.xml',
        'data/crm_claim_corrective_workflow.xml',
    ],
    'installable': True,
}
