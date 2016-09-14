# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'MRP Operations Extension Manual Close',
    'version': "8.0.1.1.0",
    'license': 'AGPL-3',
    'author': 'OdooMRP team,'
              'AvanzOSC,'
              'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    'website': "http://www.odoomrp.com",
    "contributors": [
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        ],
    'category': 'Manufacturing',
    'depends': ['mrp_operations_extension',
                'mrp_production_manual_close'
                ],
    'data': ["views/mrp_production_view.xml",
             ],
    'installable': True,
    'auto_install': True,
}
