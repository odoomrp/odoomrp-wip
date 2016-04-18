# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product configurator for stock pickings",
    "version": "8.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://www.tecnativa.com/",
    "author": "Tecnativa, "
              "OdooMRP",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
        "product_variants_no_automatic_creation",
    ],
    "data": [
        'views/stock_move_view.xml',
    ],
}
