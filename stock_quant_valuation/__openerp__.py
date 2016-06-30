# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock Quant Valuation",
    "version": "8.0.0.1.0",
    "license": "AGPL-3",
    "depends": ["mrp_production_estimated_cost", ],
    "author": "OdooMRP team",
    "category": "Warehouse management",
    'data': ["views/stock_quant_view.xml",
             "wizard/stock_valuation_history_view.xml"],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
