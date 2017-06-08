
# -*- encoding: utf-8 -*-
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Quant Expiry State Color",
    "version": "1.0",
    "depends": ["base", "product_expiry_ext"],
    "author": "OdooMRP team",
    "contributors": [
            "Pedro Manuel Baeza Romero <pedro.baeza@serviciosbaeza.com>",
            "Ana Juaristi Olalde <ajuaristio@gmail.com>",
            "Mikel Arregi <mikelarregi@avanzosc.es>"],
    "category": "Stock",
    'data': ["views/stock_quant_view.xml"],
    "installable": True,
    "auto_install": False,
}
