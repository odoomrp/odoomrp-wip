
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
    "name": "Raw Materials to Manufacturing Order Through Attributes",
    "version": "1.0",
    "depends": ["base", "mrp", "website_sale", "product_attribute_types"],
    "author": "OdooMRP team",
    "contributors": ["Mikel Arregi <mikelarregi@avanzosc.es>"],
    "category": "Manufacturing",
    'data': ["views/attribute_value_view.xml",
             "views/mrp_production_view.xml"],
    "installable": True,
    "auto_install": False,
}
