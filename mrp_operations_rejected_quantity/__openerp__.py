# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'MRP Operations Rejected Quantity',
    'version': '8.0.1.0.0',
    'category': 'Manufacturing',
    'license': "AGPL-3",
    'author': 'OdooMRP team, '
              'AvanzOSC, ',
    'website': "http://www.odoomrp.com",
    'contributors': [
        'Ana Juaristi <anajuaristi@avanzosc.es>',
        'Alfredo de la Fuente <alfredodelafuente@avanzosc.es>',
    ],
    'depends': [
        'mrp_operations_time_control',
    ],
    'data': [
        'wizard/wiz_stop_production_operation_view.xml',
        'wizard/mrp_work_order_produce_view.xml',
        'views/mrp_production_workcenter_line_view.xml',
        'views/operation_time_line_view.xml',
    ],
    "demo": [
        "demo/mrp_production_demo.xml",
    ],
    'installable': True,
}
