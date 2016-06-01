# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Repair Analytic",
    "version": "8.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "license": "AGPL-3",
    "category": "MRP Repair",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Esther Martín <esthermartin@avanzosc.es>",
    ],
    "depends": ['account',
                'analytic',
                'hr_timesheet_invoice',
                'mrp_repair',
                ],
    "data": ['security/mrp_repair_analytic_security.xml',
             'data/analytic_journal_data.xml',
             'views/mrp_repair_view.xml',
             'views/res_config_view.xml'
             ],
    "installable": True
}
