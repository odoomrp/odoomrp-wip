# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Purchase - Product variants",
    "summary": "Product variants in purchase management",
    "version": "8.0.2.1.0",
    "license": "AGPL-3",
    "depends": [
        "product",
        "purchase",
        "product_variants_no_automatic_creation",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "David Díaz <d.diazp@gmail.com>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Purchase Management",
    "website": "http://www.odoomrp.com",
    "data": [
        "views/purchase_view.xml",
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
