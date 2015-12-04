# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class PreventiveMaster(models.Model):
    _name = 'preventive.master'
    _description = 'Preventive master data'

    name = fields.Char('Name')
    pmo_type = fields.Many2one('preventive.master.type', 'Maintenance type',
                               required=True)
    machinemodel = fields.Many2one('machine.model', 'Machine Model',
                                   required=True)
    machinery_ids = fields.Many2many('machinery', 'machine_maint_rel',
                                     'preventive_master_id', 'machinery_id')
    ope_material = fields.One2many('preventive.operation.matmach', 'opmaster',
                                   'Material')
    opdescription = fields.Text('Description')


class PreventiveMasterType(models.Model):
    _name = 'preventive.master.type'
    _description = 'Preventive master data'

    name = fields.Char('Name')
    master_type = fields.Char('Type')
