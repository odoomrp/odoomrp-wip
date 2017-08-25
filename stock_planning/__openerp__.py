# -*- coding: utf-8 -*-
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Stock Planning',
    "version": "8.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,",
    'website': "http://www.odoomrp.com",
    'category': 'Warehouse Management',
    "license": 'AGPL-3',
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    'depends': ['sale',
                'purchase',
                'stock',
                'product_variant_cost_price'
                ],
    'data': ['security/stock_planning.xml',
             'security/ir.model.access.csv',
             'wizard/wiz_stock_planning_view.xml',
             'views/stock_planning_view.xml',
             'views/stock_config_settings_view.xml',
             ],
    'installable': True,
}
