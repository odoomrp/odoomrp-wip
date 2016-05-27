# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP - Task filtering wizard",
    "version": "8.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "depends": [
        "mrp",
        "project",
        "mrp_project",
    ],
    "data": [
        "views/project_task_work_view.xml",
        "wizard/wizard_filter_mrp_task_view.xml",
    ],
    "installable": True,
}
