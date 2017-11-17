# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Claims Management Corrective Measures",
    "version": "8.0.1.1.0",
    "license": "AGPL-3",
    "depends": [
        "crm_claim",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "website": "www.odoomrp.com",
    "category": "Customer Relationship Management",
    "data": [
        "security/ir.model.access.csv",
        "views/crm_claim_view.xml",
        "data/crm_claim_corrective_sequence.xml",
    ],
    "demo": [
        "demo/crm_claim_corrective_demo.xml",
    ],
    "installable": True,
}
