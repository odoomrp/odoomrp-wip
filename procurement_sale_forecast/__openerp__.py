# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "MPS - Sale forecast",
    "version": "8.0.1.1.0",
    "depends": [
        "base",
        "product",
        "sale",
        "stock",
    ],
    "license": "AGPL-3",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Daniel Campos <danielcampos@avanzosc.es>",
    ],
    "category": "MPS",
    "website": "http://www.odoomrp.com",
    "summary": "Sale forecast",
    "data": ["security/ir.model.access.csv",
             "wizard/sale_forecast_load_view.xml",
             "views/sale_view.xml",
             ],
    "installable": True,
    "auto_install": False,
}
