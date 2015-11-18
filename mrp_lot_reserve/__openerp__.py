# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Lot Reserve",
    "version": "8.0.1.1.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "mrp_production_editable_scheduled_products",
    ],
    "data": [
        "views/mrp_production_view.xml",
    ],
    "installable": True,
}
