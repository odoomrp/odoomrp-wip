# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale Order Allowed Product",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa",
    "website": "http://www.odoomrp.com",
    "category": "Sales Management",
    "depends": [
        "base",
        "sale",
        "product_supplierinfo_for_customer",
    ],
    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
