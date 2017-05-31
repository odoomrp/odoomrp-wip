# -*- coding: utf-8 -*-
# (c) 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Quality Control - MRP operations",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>"
    ],
    "category": "Quality control",
    "depends": [
        "mrp_operations_extension",
        "quality_control",
    ],
    "data": [
        "views/qc_inspection_view.xml",
        "views/mrp_routing_operation_view.xml",
        "views/mrp_production_workcenter_line_view.xml",
        "views/mrp_routing_workcenter_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
