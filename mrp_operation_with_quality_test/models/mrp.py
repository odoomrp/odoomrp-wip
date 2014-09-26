
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 12/09/2014
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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class MrpRoutingOperation(models.Model):
    _inherit = 'mrp.routing.operation'

    required_test = fields.Boolean(string='Required Test')
    qtemplate_id = fields.Many2one('qc.test.template', string='Test Template')
    analytic_journal_id = fields.Many2one('account.analytic.journal',
                                          string='Analytic Journal')

    @api.model
    def create(self, data):
        if 'required_test' in data:
            required_test = data.get('required_test')
            if required_test:
                if 'qtemplate_id' not in data:
                    raise except_orm(_('Operation Creation Error!'),
                                     _("You must define the test template"))
                else:
                    qtemplate_id = data.get('required_test')
                    if not qtemplate_id:
                        raise except_orm(_('Operation Creation Error!'),
                                         _("You must define template test"))
            else:
                data.update({'qtemplate_id': False})
        return super(MrpRoutingOperation, self).create(data)

    @api.one
    def write(self, vals):
        if 'required_test' in vals:
            required_test = vals.get('required_test')
            if required_test:
                if 'qtemplate_id' not in vals:
                    raise except_orm(_('Operation Modification Error!'),
                                     _("You must define the test template"))
                else:
                    qtemplate_id = vals.get('required_test')
                    if not qtemplate_id:
                        raise except_orm(_('Operation Modification Error!'),
                                         _("You must define template test"))
            else:
                vals.update({'qtemplate_id': False})
        return super(MrpRoutingOperation, self).write(vals)


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    required_test = fields.Boolean(string='Required Test')
    qtemplate_id = fields.Many2one('qc.test.template', string='Test Template')
    test_ids = fields.One2many('qc.test', 'workcenter_line_id',
                               string='Quality Tests')
    analytic_journal_id = fields.Many2one('account.analytic.journal',
                                          string='Analytic Journal')

    @api.model
    def create(self, data):
        workcenter_obj = self.env['mrp.routing.workcenter']
        find_test = False
        if 'required_test' in data:
            required_test = data.get('required_test')
            if required_test:
                if 'qtemplate_id' not in data:
                    raise except_orm(_('Error!'),
                                     _("You must define the test template"))
                else:
                    qtemplate_id = data.get('required_test')
                    if not qtemplate_id:
                        raise except_orm(_('Error!'),
                                         _("You must define template test"))
            else:
                find_test = True
                data.update({'qtemplate_id': False})
        else:
            data.update({'qtemplate_id': False})
            find_test = True
        if find_test:
            if 'routing_wc_line' in data:
                routing_wc_line_id = data.get('routing_wc_line')
                work = workcenter_obj.browse(routing_wc_line_id)
                data.update({'required_test': work.operation.required_test})
                if work.operation.qtemplate_id:
                    data.update({'qtemplate_id':
                                 work.operation.qtemplate_id.id})
                if work.operation.analytic_journal_id:
                    data.update({'analytic_journal_id':
                                 work.operation.analytic_journal_id.id})
        return super(MrpProductionWorkcenterLine, self).create(data)

    @api.one
    def write(self, vals, update=False):
        if 'required_test' in vals:
            required_test = vals.get('required_test')
            if required_test:
                if 'qtemplate_id' not in vals:
                    raise except_orm(_('Operation Modification Error!'),
                                     _("You must define the test template"))
                else:
                    qtemplate_id = vals.get('required_test')
                    if not qtemplate_id:
                        raise except_orm(_('Operation Modification Error!'),
                                         _("You must define template test"))
            else:
                vals.update({'qtemplate_id': False})
        return super(MrpProductionWorkcenterLine, self).write(vals,
                                                              update=update)

    @api.one
    @api.model
    def create_quality_test(self):
        test_obj = self.env['qc.test']
        vals = {'workcenter_line_id': self.id,
                'test_template_id': self.qtemplate_id.id,
                }
        if self.qtemplate_id.object_id:
            vals.update({'object_id': self.qtemplate_id.object_id.id})
        test = test_obj.create(vals)
        test.set_test_template(self.qtemplate_id.id)
        return True

    @api.one
    @api.model
    def action_start_working(self):
        result = super(MrpProductionWorkcenterLine,
                       self).action_start_working()
        self.create_quality_test()
        return result

    @api.one
    @api.model
    def action_done(self):
        if self.test_ids:
            for test in self.test_ids:
                if test.state not in ('success', 'failed', 'canceled'):
                    raise except_orm(_('Finalization Operation Error!'),
                                     _("The Operation has quality test without"
                                       "QUALITY SUCCESS state"))
        return super(MrpProductionWorkcenterLine, self).action_done()
