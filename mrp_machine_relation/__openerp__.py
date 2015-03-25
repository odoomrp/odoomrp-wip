
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "MRP Machine Relation",
    "version": "1.0",
    "category": "Manufacturing",
    "description": """
    This modules links mrp.workcenters and machines. Also adds the machine
    users to the workcenter operators.
    """,
    "author": "OdooMRP team,"
              "Avanzosc,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": ["Daniel Campos <danielcampos@avanzosc.es>"],
    "website": "http://www.odoomrp.com",
    "depends": [
        "mrp_operations_extension",
        "machine_manager",
    ],
    "data": ["views/mrp_workcenter_view.xml"],
    "installable": True,
    "auto_install": True,
}
