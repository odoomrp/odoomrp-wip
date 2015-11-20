# -*- coding: utf-8 -*-
# (c) 2014-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Quality control - Samples in inspections",
    "version": "8.0.1.1.0",
    "depends": [
        "quality_control",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "Quality control",
    'demo': [
        'demo/qc_sample_demo.xml',
        'demo/qc_test_demo.xml',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/qc_sample_view.xml',
        'views/qc_test_view.xml',
        'views/qc_inspection_view.xml',
    ],
    'installable': True,
}
