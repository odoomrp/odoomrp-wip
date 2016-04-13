# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Procurement Plan",
    "version": "8.0.1.0.0",
    "author": "Odoo Community Association (OCA),"
              "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Procurements",
    "license": 'AGPL-3',
    "depends": ['stock',
                'procurement',
                'project',
                'purchase',
                'sale_stock',
                'mail',
                'procurement_manager'
                ],
    "data": ['data/sequence.xml',
             'security/procurement_plan.xml',
             'wizard/wiz_import_procurement_from_plan_view.xml',
             'wizard/wiz_load_sale_from_plan_view.xml',
             'wizard/wiz_load_purchase_from_plan_view.xml',
             'wizard/wiz_change_procurement_date_view.xml',
             'views/procurement_view.xml',
             'views/procurement_view.xml',
             'views/procurement_plan_view.xml',
             ],
    "installable": True
}
