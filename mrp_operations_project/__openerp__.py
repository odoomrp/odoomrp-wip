# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Project Link - Operations",
    "summary": "Link production with projects - Operations bridge",
    "version": "8.0.1.0.0",
    "depends": [
        "mrp_project_link",
        "mrp_operations_extension",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category": "Manufacturing",
    'data': [
        "views/project_task_view.xml"
    ],
    'installable': True,
    'auto_install': True,
}
