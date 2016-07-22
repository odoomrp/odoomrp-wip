# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui (AvanzOSC)
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Variants",
    "version": "8.0.2.1.1",
    "depends": [
        "product",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Tecnativa",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Product Variant",
    "website": "http://www.odoomrp.com",
    "summary": "Disable automatic product variant creation",
    "data": [
        "views/product_attribute_price_view.xml",
        "views/product_category_view.xml",
        "views/product_configurator_view.xml",
        "views/product_product_view.xml",
        "views/product_template_view.xml",
        "security/ir.model.access.csv",
        "security/product_configurator_security.xml",
    ],
    "installable": True,
}
