
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
