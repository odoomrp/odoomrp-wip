# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Quality control version",
    "summary": "Quality test versioning",
    "version": "8.0.1.1.0",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "quality_control",
    ],
    "data": [
        "views/qc_test_view.xml",
    ],
    "installable": True,
    "post_init_hook": "populate_unrevisioned_name",
}
