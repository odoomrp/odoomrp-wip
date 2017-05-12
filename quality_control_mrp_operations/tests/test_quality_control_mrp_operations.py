# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions


class TestQualityControlMrpOperations(common.TransactionCase):

    def setUp(self):
        super(TestQualityControlMrpOperations, self).setUp()
        self.routing_operation_model = self.env['mrp.routing.operation']
        self.workcenter_line_model = self.env['mrp.production.workcenter.line']
        self.routing_workcenter = (
            self.browse_ref('mrp.mrp_routing_workcenter_0'))

    def test_quality_control_mrp_operations(self):
        vals = {'name': 'Operation quality control',
                'required_test': True}
        with self.assertRaises(exceptions.Warning):
            self.routing_operation_model.create(vals)
        vals['qtemplate_id'] = False
        with self.assertRaises(exceptions.Warning):
            self.routing_operation_model.create(vals)
        vals['qtemplate_id'] = self.ref('quality_control.qc_test_1')
        routing_operation = self.routing_operation_model.create(vals)
        vals = {'name': 'Operation quality control',
                'required_test': True}
        with self.assertRaises(exceptions.Warning):
            routing_operation.write(vals)
        vals['qtemplate_id'] = False
        with self.assertRaises(exceptions.Warning):
            routing_operation.write(vals)
        vals['qtemplate_id'] = self.ref('quality_control.qc_test_1')
        routing_operation.write(vals)
        self.routing_workcenter.qtemplate_ids = (
            [(6, 0, [self.ref('quality_control.qc_test_1')])])
        vals = {'routing_wc_line': self.routing_workcenter.id,
                'required_test': True}
        with self.assertRaises(exceptions.Warning):
            self.workcenter_line_model.create(vals)
        vals['qtemplate_id'] = False
        with self.assertRaises(exceptions.Warning):
            self.workcenter_line_model.create(vals)
        self.routing_workcenter.operation = routing_operation.id
        vals = {'name': 'Workcenter line for quality control mrp operations',
                'production_id':
                self.ref('mrp_operations_extension.mrp_production_opeext'),
                'workcenter_id': self.ref('mrp.mrp_workcenter_0'),
                'routing_wc_line': self.routing_workcenter.id}
        workcenter_line = self.workcenter_line_model.create(vals)
        vals = {'required_test': True}
        with self.assertRaises(exceptions.Warning):
            workcenter_line.write(vals)
        vals['qtemplate_id'] = False
        with self.assertRaises(exceptions.Warning):
            workcenter_line.write(vals)
        workcenter_line.production_id.state = 'in_production'
        workcenter_line.action_start_working()
        self.assertEquals(workcenter_line.ope_tests, 2,
                          'Bad quality test creation')
        with self.assertRaises(exceptions.Warning):
            workcenter_line.action_done()
