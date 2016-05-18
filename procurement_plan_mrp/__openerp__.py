# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Procurement Plan MRP",
    "version": "8.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Manufacturing",
    "license": 'AGPL-3',
    "depends": ['base',
                'product',
                'stock',
                'sale',
                'mrp',
                'procurement_plan',
                'stock_reserve',
                'sale_mrp_project_link',
                ],
    "data": ['wizard/wiz_change_procurement_date_planned_view.xml',
             'views/mrp_production_view.xml',
             'views/procurement_plan_view.xml',
             'views/procurement_order_view.xml',
             'views/stock_reservation_view.xml',
             ],
    "installable": True
}
