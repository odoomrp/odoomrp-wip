
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Manufacturing Order Resume",
    "version": "1.0",
    "depends": ["base", "mrp_operations_extension", "crm_claim",
                "product_packaging_views"],
    "author": "OdooMRP team",
    "contributors": ["Mikel Arregi <mikelarregi@avanzosc.es>"],
    "category": "Manufacturing",
    "description": """
    This module provides an association between the bulk product and
    the way it must be packaged at the end of the bulk product manufacturing.

    Particularly suitable for chemical industries and
    others that produce liquid finished products.
    """,
    'data': ["views/mrp_operations.view.xml",
             "views/attribute_value_view.xml"],
    "installable": True,
    "auto_install": False,
}
