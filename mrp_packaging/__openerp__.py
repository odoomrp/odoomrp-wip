# -*- coding: utf-8 -*-
# © 2015 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Manufacturing order from packaging summary",
    "version": "8.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "base",
        "mrp_product_variants",
        "mrp_bom_through_attributes",
        "mrp_lot_reserve",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mrp_packaging_data.xml",
        "views/mrp_production_view.xml",
    ],
    "installable": True,
}
