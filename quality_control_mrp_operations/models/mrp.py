# -*- coding: utf-8 -*-
# (c) 2016 Oihane Crucelaegui - AvanzOSC
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


class MrpRoutingOperation(models.Model):
    _inherit = 'mrp.routing.operation'

    required_test = fields.Boolean(string='Required test')
    qtemplate_id = fields.Many2one('qc.test', string='Test')

    @api.model
    def create(self, data):
        if 'required_test' in data:
            required_test = data.get('required_test')
            if required_test:
                if 'qtemplate_id' not in data:
                    raise exceptions.Warning(
                        _('Operation Creation Error!, You must define the test'
                          ' template'))
                else:
                    qtemplate_id = data.get('qtemplate_id')
                    if not qtemplate_id:
                        raise exceptions.Warning(
                            _('Operation Creation Error!, You must define '
                              'template test'))
            else:
                data.update({'qtemplate_id': False})
        return super(MrpRoutingOperation, self).create(data)

    @api.one
    def write(self, vals):
        if 'required_test' in vals:
            required_test = vals.get('required_test')
            if required_test:
                if 'qtemplate_id' not in vals:
                    raise exceptions.Warning(
                        _('Operation Modification Error!, You must define the '
                          'test template'))
                else:
                    qtemplate_id = vals.get('qtemplate_id')
                    if not qtemplate_id:
                        raise exceptions.Warning(
                            _('Operation Modification Error! You must define '
                              'template test'))
            else:
                vals.update({'qtemplate_id': False})
        return super(MrpRoutingOperation, self).write(vals)


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.one
    @api.onchange('test_ids')
    def _count_tests(self):
        self.ope_tests = len(self.test_ids)

    required_test = fields.Boolean(string='Required Test')
    qtemplate_id = fields.Many2one('qc.test', string='Test')
    test_ids = fields.One2many('qc.inspection', 'workcenter_line_id',
                               string='Quality Tests')
    ope_tests = fields.Integer(string="Created inspections",
                               compute='_count_tests')
    routing_workcenter_qtemplate_ids = fields.Many2many(
        comodel_name='qc.test', string='Quality tests from routing')

    @api.model
    def create(self, data):
        workcenter_obj = self.env['mrp.routing.workcenter']
        if data.get('routing_wc_line', False):
            work = workcenter_obj.browse(data.get('routing_wc_line'))
            if work.qtemplate_ids:
                data.update({'routing_workcenter_qtemplate_ids':
                             [(6, 0, work.qtemplate_ids.ids)]})
        find_test = False
        if data.get('required_test', False):
            if not data.get('qtemplate_id', False):
                raise exceptions.Warning(
                    _('Error!, You must define the test template'))
        else:
            data.update({'qtemplate_id': False})
            find_test = True
        if find_test:
            if 'routing_wc_line' in data:
                data.update({'required_test': work.operation.required_test})
                if work.operation.qtemplate_id:
                    data.update({'qtemplate_id':
                                 work.operation.qtemplate_id.id})
        return super(MrpProductionWorkcenterLine, self).create(data)

    @api.one
    def write(self, vals, update=False):
        if 'required_test' in vals:
            if vals.get('required_test'):
                if not vals.get('qtemplate_id', False):
                    raise exceptions.Warning(
                        _('Operation Modification Error!, You must define the '
                          'test template'))
            else:
                vals.update({'qtemplate_id': False})
        return super(MrpProductionWorkcenterLine, self).write(vals,
                                                              update=update)

    @api.one
    @api.model
    def create_quality_test(self, qtemplate):
        vals = {
            'workcenter_line_id': self.id,
            'test': qtemplate.id,
        }
        if qtemplate.object_id:
            vals['object_id'] = "%s,%s" % (
                qtemplate.object_id._name, qtemplate.object_id.id)
        inspection = self.env['qc.inspection'].create(vals)
        inspection.inspection_lines = inspection._prepare_inspection_lines(
            qtemplate)
        return True

    @api.one
    @api.model
    def action_start_working(self):
        result = super(MrpProductionWorkcenterLine,
                       self).action_start_working()
        if self.routing_workcenter_qtemplate_ids:
            for qtemplate in self.routing_workcenter_qtemplate_ids:
                self.create_quality_test(qtemplate)
        if self.required_test:
            self.create_quality_test(self.qtemplate_id)
        return result

    @api.one
    @api.model
    def action_done(self):
        if self.test_ids:
            for test in self.test_ids:
                if test.state not in ('success', 'failed', 'canceled'):
                    raise exceptions.Warning(
                        _('Finalization Operation Error!, There are quality '
                          'tests in draft or approval pending state for this '
                          'operation. Please finish or cancel them.'))
        return super(MrpProductionWorkcenterLine, self).action_done()


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    qtemplate_ids = fields.Many2many(
        comodel_name='qc.test', string='Quality tests')
