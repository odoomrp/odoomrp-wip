# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestMrpProductionMachineLocation(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionMachineLocation, self).setUp()
        self.machine = self.env.ref('machine_manager.machinery_1')
        self.machine.location = self.ref('stock.location_refrigerator_small')
        self.workcenter = self.env.ref('mrp.mrp_workcenter_0')
        self.workcenter.machine = self.machine.id
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')

    def test_mrp_production_machine_location(self):
        self.assertEqual(self.production.state, 'draft')
        self.production.signal_workflow('button_confirm')
        stock_moves = self.production.mapped('move_lines').filtered(
            lambda l: l.work_order.workcenter_id == self.workcenter)
        for stock_move in stock_moves:
            self.assertEqual(
                stock_move.location_id, self.machine.location,
                'products to consume without machine location')
        stock_moves.write(
            {'location_id':
             self.ref('stock.stock_location_locations_virtual')})
        stock_moves.action_confirm()
        for stock_move in stock_moves:
            self.assertEqual(
                stock_move.location_id, self.machine.location,
                'products to consume without machine location')
