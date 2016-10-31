# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestMrpOperationsRejectedQuantity(common.TransactionCase):

    def setUp(self):
        super(TestMrpOperationsRejectedQuantity, self).setUp()
        self.workcenter = self.env['mrp.workcenter'].create(
            {'name': 'Test work center',
             'op_number': 1,
             'capacity_per_cycle': 5,
             'capacity_per_cycle_min': 1,
             'time_cycle': 1.0}
        )
        self.operation = self.env['mrp.routing.operation'].create(
            {'name': 'Test operation',
             'op_number': 2,
             'workcenters': [(6, 0, self.workcenter.ids)]})
        self.routing = self.env['mrp.routing'].create(
            {'name': 'Test routing'})
        self.routing_workcenter = self.env['mrp.routing.workcenter'].create(
            {
                'name': 'Test routing line',
                'do_production': True,
                'workcenter_id': self.workcenter.id,
                'routing_id': self.routing.id,
            })
        self.operation_workcenter = (
            self.env['mrp.operation.workcenter'].create(
                {
                    'workcenter': self.workcenter.id,
                    'routing_workcenter': self.routing_workcenter.id,
                    'default': True,
                }))
        self.production_model = self.env['mrp.production']
        self.work_order_produce_model = self.env['mrp.work.order.produce']
        self.produce_line_model = self.env['mrp.product.produce.line']
        self.stop_model = self.env['wiz.stop.production.operation']
        self.production = self.env.ref(
            'mrp_operations_rejected_quantity.mrp_production_rejectedquantity')

    def test_mrp_operations_rejected_quantity(self):
        self.production.signal_workflow('button_confirm')
        self.production.force_production()
        operation = self.production.workcenter_lines[0]
        operation.signal_workflow('button_start_working')
        self.assertEqual(
            operation.state, 'startworking',
            'Error work center line not in start working state')
        stop_vals = {
            'employee_id': self.ref('hr.employee_chs'),
            'accepted_amount': 1,
            'rejected_amount': 1,
            'stop_date': '2025-01-23'}
        wiz_stop = self.stop_model.with_context(
            {'active_id': operation.id}).create(stop_vals)
        wiz_stop.with_context(
            {'active_id': operation.id}).default_get([])
        wiz_stop.with_context(
            {'active_id': operation.id}).stop_operation()
        self.assertEqual(
            operation.operation_time_lines[0].employee_id.id,
            self.ref('hr.employee_chs'), 'Operation time without employee')
        consume = self.work_order_produce_model.with_context(
            active_ids=[operation.id], active_id=operation.id).create({})
        result = consume.with_context(
            active_ids=[operation.id], active_id=operation.id).on_change_qty(
            consume.product_qty, [])
        if 'value' in result:
            if ('consume_lines' in result['value'] and
                    result['value']['consume_lines']):
                for cl in result['value']['consume_lines']:
                    consu_vals = cl[2]
                    consu_vals['work_produce_id'] = consume.id
                    self.produce_line_model.create(consu_vals)
        if not consume.final_product:
            consume.with_context(active_id=operation.id).do_consume()
        else:
            consume.with_context(active_id=operation.id).do_consume_produce()
        consume._catch_consume_lines(operation)
        for line in operation.operation_time_lines:
            line._compute_total_amount()
        self.assertEqual(
            operation.operation_time_lines.state, 'processed',
            'Operation time line not in processed state')
