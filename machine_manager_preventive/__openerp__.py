# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Machine manager preventive",
    "version": "8.0.1.0.0",
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
