# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestMrpProductionMachineLocation(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionMachineLocation, self).setUp()
        self.location = self.env['stock.location'].create({
            'name': 'Test Location',
        })
        self.machine = self.env['machinery'].create({
            'name': 'Test Machine',
            'location': self.location.id,
        })
        self.workcenter = self.browse_ref('mrp.mrp_workcenter_0')
        self.workcenter.machine = self.machine.id
        self.production = self.browse_ref(
            'mrp_operations_extension.mrp_production_opeext')

    def test_mrp_production_machine_location(self):
        self.assertEqual(self.production.state, 'draft')
        self.production.signal_workflow('button_confirm')
        for consume_line in self.production.mapped('move_lines').filtered(
                lambda l: l.work_order.workcenter_id.machine.location):
            self.assertEquals(
                consume_line.location_id,
                consume_line.work_order.workcenter_id.machine.location)
            self.assertEquals(consume_line.location_id,
                              self.machine.location)
            self.assertEquals(consume_line.location_id,
                              self.location)
