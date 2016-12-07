# -*- coding: utf-8 -*-
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

{
    "name": "Product Packaging through Attributes",
    "version": "9.0.1.0.0",
    "depends": [
        "product_packaging_views",
        "product_attribute_types",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Tecnativa",
    "website": "http://www.odoomrp.com",
    "category": "Custom Module",
    "data": [
        "views/product_view.xml",
        "views/res_partner_view.xml",
    ],
    'installable': True,
    'license': 'AGPL-3',
}
