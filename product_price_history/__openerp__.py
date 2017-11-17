# -*- coding: utf-8 -*-
# (c) 2013 Joel Grand-Guillaume - Camptocamp SA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Product Price History",
    "version": "8.0.2.0.0",
    "category": "Generic Modules/Inventory Control",
    "license": "AGPL-3",
    "author": "Camptocamp, "
              "OdooMRP team, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "AvanzOSC",
    "contributors": [
        "Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>",
        "Yannick Vaucher <yannick.vaucher@camptocamp.com>",
        "Pedro M. Baeza <pedro.baeza@serviciobaeza.com> (Migration to v8)",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "product",
        "product_variant_cost_price",
    ],
    "data": [
        "views/product_price_history_view.xml",
        "views/product_product_view.xml",
    ],
    "installable": True,
}
