# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields


class StepConfigLine(orm.Model):
    _name = 'step.config.line'

    _columns = {
        'sequence': fields.integer('Sequence'),
        'group_id': fields.many2one('res.groups', 'Security Group'),
        'step_id': fields.many2one('step.config', 'Config Step',
                                   required=True),
        'button': fields.char('Button Text', size=64),
    }


class StepConfig(orm.Model):
    _name = 'step.config'

    _columns = {
        'model_id': fields.many2one('ir.model', 'Model'),
        'line_ids': fields.one2many('step.config.line', 'step_id', 'Lines'),
    }
