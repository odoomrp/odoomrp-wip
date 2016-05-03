# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Purchase Order Allowed Product",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Purchase Management",
    "depends": [
        "base",
        "product",
        "purchase",
    ],
    "data": [
        "views/res_partner_view.xml",
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
