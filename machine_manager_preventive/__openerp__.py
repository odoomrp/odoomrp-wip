
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
    "name": "Machine manager preventive",
    "version": "1.0",
    "depends": ["machine_manager", "mrp_repair"],
    "author": "OdooMRP team",
    "website": "http://www.odoomrp.com",
    "contributors": ["Daniel Campos <danielcampos@avanzosc.es>",
                     "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
                     "Ana Juaristi <ajuaristio@gmail.com>"],
    "category": "Manufacturing",
    "data": ["security/preventive_manager_security.xml",
             "security/ir.model.access.csv",
             "wizard/create_preventive_wizard_view.xml",
             "wizard/create_repair_order_wizard_view.xml",
             "views/preventive_mrp_data.xml",
             "views/preventive_sequence.xml",
             "views/machine_view.xml",
             "views/preventive_master_view.xml",
             "views/preventive_operation_view.xml",
             "views/preventive_machine_operation_view.xml",
             "views/mrp_repair_view.xml"],
    "installable": True
}
