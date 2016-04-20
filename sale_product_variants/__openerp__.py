# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale - Product variants",
    "summary": "Product variants in sale management",
    "version": "8.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "product",
        "sale",
        "product_variants_no_automatic_creation",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Sales Management",
    "website": "http://www.odoomrp.com",
    "data": [
        "views/sale_view.xml",
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
