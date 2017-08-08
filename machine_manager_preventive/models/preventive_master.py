# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class PreventiveMaster(models.Model):
    _name = 'preventive.master'
    _description = 'Preventive master data'

    name = fields.Char(string='Name')
    pmo_type = fields.Many2one(comodel_name='preventive.master.type',
                               string="Preventive master type",
                               inverse_name='Maintenance type', required=True)
    machinemodel = fields.Many2one(comodel_name='machine.model',
                                   string='Machine Model', required=True)
    machinery_ids = fields.Many2many(
        comodel_name='machinery', relation='machine_maint_rel',
        column1='preventive_master_id', column2='machinery_id')
    ope_material = fields.One2many(comodel_name='preventive.operation.matmach',
                                   inverse_name='opmaster', string='Material')
    opdescription = fields.Text(string='Description')


class PreventiveMasterType(models.Model):
    _name = 'preventive.master.type'
    _description = 'Preventive master type'

    name = fields.Char(string='Name')
    master_type = fields.Char(string='Type')
