# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
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
    "name": "Warning Log",
    "version": "1.0",
    "depends": ["base", "warning"],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "contributors": ["Mikel Arregi <mikelarregi@avanzosc.es>"],
    "category": "Tools",
    "description": """
This module provide :
    New menu entry with log of warnigs raised by "warning" module
    """,
    'data': [
        "views/warning_log_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
