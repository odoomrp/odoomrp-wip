# -*- coding: utf-8 -*-
#    2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
#    2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Stock picking package info",
    "version": "8.0.1.1.0",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Inventory, Logistic, Storage",
    "depends": [
        "product",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/stock_transfer_details_view.xml",
        "views/stock_quant_package_view.xml",
        "views/stock_picking_view.xml",
        "reports/label_creator_palet_report.xml"
    ],
    "installable": True,
}
