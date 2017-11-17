# -*- coding: utf-8 -*-
# (c) 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions


class TestMrpRepairAnalytic(common.TransactionCase):

    def setUp(self):
        super(TestMrpRepairAnalytic, self).setUp()
        self.mrp_repair_model = self.env['mrp.repair']
        self.analytic_account_model = self.env['account.analytic.account']
        self.analytic_line_model = self.env['account.analytic.line']
        self.lot_model = self.env['stock.production.lot']
        self.location_model = self.env['stock.location']
        self.quant_model = self.env['stock.quant']
        analytic_vals = {
            'name': 'Repair Cost Account',
            'type': 'normal',
            }
        self.analytic_id = self.analytic_account_model.create(analytic_vals)
        # Product: Webcam -- Standard Price: 38.0
        self.op_product = self.env.ref('product.product_product_34')
        default_location = self.mrp_repair_model._default_stock_location()
        op_val = {
            'product_id': self.op_product.id,
            'product_uom_qty': 3,
            'name': self.op_product.name,
            'product_uom': self.op_product.uom_id.id,
            'type': 'add',
            'location_id': default_location,
            'location_dest_id': self.op_product.property_stock_production.id,
            'price_unit': 1,
            'to_invoice': True,
            'load_cost': True,
            }
        self.op2_product = self.env.ref('product.product_product_35')
        op_val2 = {
            'product_id': self.op2_product.id,
            'product_uom_qty': 3,
            'name': self.op2_product.name,
            'product_uom': self.op2_product.uom_id.id,
            'type': 'add',
            'location_id': default_location,
            'location_dest_id': self.op2_product.property_stock_production.id,
            'price_unit': 1,
            'to_invoice': True,
            'load_cost': True,
            }
        self.op_amount = (-1 * self.op_product.standard_price * 3)
        # Product: On Site Monitoring -- Standard Price: 20.5
        self.fee_product = self.env.ref('product.product_product_1')
        fee_val = {
            'product_id': self.fee_product.id,
            'product_uom_qty': 10,
            'name': self.fee_product.name,
            'product_uom': self.fee_product.uom_id.id,
            'price_unit': 1,
            'to_invoice': True,
            'load_cost': True,
            }
        self.fee_amount = (-1 * self.fee_product.standard_price * 10)
        self.repair_product = self.env.ref('product.product_product_27')
        repair_vals = {
            'analytic_account': self.analytic_id.id,
            'product_uom': self.repair_product.uom_id.id,
            'product_id': self.repair_product.id,
            'partner_id': self.env.ref('base.res_partner_8').id,
            'location_id': default_location,
            'location_dest_id': default_location,
            'operations': [(0, 0, op_val), (0, 0, op_val2)],
            'fees_lines': [(0, 0, fee_val)],
            'invoice_method': 'after_repair',
            'partner_invoice_id': self.env.ref('base.res_partner_8').id
            }
        self.mrp_repair = self.mrp_repair_model.create(repair_vals)

    def test_mrp_repair_create_cost_button(self):
        self.mrp_repair.signal_workflow('repair_confirm')
        self.mrp_repair.create_repair_cost()
        ope_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.op_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.op_amount)])
        fee_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.fee_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.fee_amount)])
        self.assertNotEqual(len(ope_line), 0, "Operation line cost not found.")
        self.assertNotEqual(len(fee_line), 0, "Fee line cost not found.")

    def test_mrp_repair_no_load_cost(self):
        self.mrp_repair.operations.write({'load_cost': False})
        self.mrp_repair.fees_lines.write({'load_cost': False})
        self.mrp_repair.signal_workflow('repair_confirm')
        self.mrp_repair.create_repair_cost()
        ope_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.op_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.op_amount)])
        fee_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.fee_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.fee_amount)])
        self.assertEqual(len(ope_line), 0, "Operation line cost found.")
        self.assertEqual(len(fee_line), 0, "Fee line cost found.")

    def test_mrp_repair_end_create_cost(self):
        self.mrp_repair.signal_workflow('repair_confirm')
        self.mrp_repair.signal_workflow('repair_ready')
        self.mrp_repair.signal_workflow('action_repair_end')
        ope_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.op_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.op_amount)])
        fee_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.fee_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.fee_amount)])
        self.assertNotEqual(len(ope_line), 0, "Operation line cost not found.")
        self.assertNotEqual(len(fee_line), 0, "Fee line cost not found.")

    def test_mrp_repair_cero_amount_cost(self):
        self.op_product.cost_method = 'average'
        self.op_product.standard_price = 0
        for op in self.mrp_repair.operations:
            if op.product_id == self.op_product:
                op.product_uom_qty = 12
        self.mrp_repair.signal_workflow('repair_confirm')
        self.mrp_repair.create_repair_cost()
        ope_line = self.analytic_line_model.search(
            [('account_id', '=', self.analytic_id.id),
             ('product_id', '=', self.op_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', 0)])
        self.assertEqual(len(ope_line), 0,
                         "Operation line cost with amount 0 found.")
        self.assertFalse(
            self.mrp_repair._catch_repair_line_information_for_analytic(
                self.mrp_repair.operations[0]))

    def test_mrp_repair_create_cost_no_analytic_account(self):
        self.mrp_repair.analytic_account = False
        self.mrp_repair.signal_workflow('repair_confirm')
        self.mrp_repair.create_repair_cost()
        ope_line = self.analytic_line_model.search(
            [('account_id', '=', False),
             ('product_id', '=', self.op_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.op_amount)])
        fee_line = self.analytic_line_model.search(
            [('account_id', '=', False),
             ('product_id', '=', self.fee_product.id),
             ('is_repair_cost', '=', True),
             ('amount', '=', self.fee_amount)])
        self.assertEqual(len(ope_line), 0, "Operation line cost not found.")
        self.assertEqual(len(fee_line), 0, "Fee line cost not found.")

    def test_mrp_repair_create_cost_no_journal(self):
        self.env.ref('mrp.analytic_journal_repair').unlink()
        self.mrp_repair.signal_workflow('repair_confirm')
        with self.assertRaises(exceptions.Warning):
            self.mrp_repair.create_repair_cost()

    def test_mrp_repair_invoice_crete(self):
        self.mrp_repair.signal_workflow('repair_confirm')
        self.mrp_repair.action_invoice_create()
        for line in self.mrp_repair.operations:
            self.assertEqual(
                line.invoice_line_id.account_analytic_id, self.analytic_id,
                "Wrong analytic account in the operation invoice line.")
        for line in self.mrp_repair.fees_lines:
            self.assertEqual(
                line.invoice_line_id.account_analytic_id, self.analytic_id,
                "Wrong analytic account in the fee invoice line.")

    def test_mrp_repair_line_cost(self):
        self.op2_product.cost_method = 'real'
        internal_location = self.location_model.search([('usage', '=',
                                                         'internal')], limit=1)
        lot_id = self.lot_model.create(
            {'product_id': self.op2_product.id,
             'name': 'LOT-TEST'})
        self.quant_model.create(
            {'product_id': self.op2_product.id,
             'lot_id': lot_id.id,
             'cost': 11,
             'location_id': internal_location.id,
             'qty': 5})
        line = self.mrp_repair.operations.filtered(
            lambda x: x.product_id == self.op2_product)
        line.lot_id = lot_id
        for operation in self.mrp_repair.operations:
            cost = 0
            if operation.product_id.cost_method == 'real' and operation.lot_id:
                quants = operation.lot_id.quant_ids.filtered(
                    lambda x: x.location_id.usage == 'internal')
                if quants:
                    cost = quants[:1].cost
            else:
                cost = operation.product_id.standard_price
            self.assertEqual(operation.standard_price, cost,
                             "Operation line cost is not correct.")
