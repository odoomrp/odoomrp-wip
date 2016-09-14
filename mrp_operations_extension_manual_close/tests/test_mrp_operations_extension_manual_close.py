# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpOperationsExtensionManualClose(common.TransactionCase):

    def setUp(self):
        super(TestMrpOperationsExtensionManualClose, self).setUp()
        self.production_wiz = self.env['mrp.product.produce']
        self.production_finish_wiz = self.env['workcenter.line.finish']
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')
        self.production.product_qty = 5
        self.production.signal_workflow('button_confirm')
        self.production.force_production()

    def test_production_close_partial_production(self):
        self.wiz = self.production_wiz.with_context(
            active_id=self.production.id).create(
                {'product_id': self.production.product_id.id,
                 'product_qty': 2,
                 })
        self.wiz.with_context(active_id=self.production.id).do_produce()
        res = self.production.button_produce_close()
        self.assertEqual(res.get('res_model', False), 'workcenter.line.finish',
                         'Finish wizard not launched.')

    def test_production_close_complete_production(self):
        self.wiz = self.production_wiz.with_context(
            active_id=self.production.id).create(
                {'product_id': self.production.product_id.id,
                 'product_qty': 5,
                 })
        self.wiz.with_context(active_id=self.production.id).do_produce()
        res = self.production.button_produce_close()
        self.assertEqual(res, {}, 'Finish wizard launched.')
        self.assertEqual(self.production.state, 'done',
                         'Error production not finished.')

    def test_finish_wizard_cancel(self):
        self.wiz = self.production_wiz.with_context(
            active_id=self.production.id).create(
                {'product_id': self.production.product_id.id,
                 'product_qty': 2,
                 })
        self.wiz.with_context(active_id=self.production.id).do_produce()
        move_lines = self.production.move_lines
        dest_move_lines = self.production.move_created_ids
        finish_wizard = self.production_finish_wiz.with_context(
            active_model='mrp.production',
            active_id=self.production.id).create({})
        finish_wizard.cancel_all()
        self.assertFalse(move_lines.filtered(lambda x: x.state != 'cancel'),
                         'Moves state is not cancel.')
        self.assertFalse(dest_move_lines.filtered(lambda x:
                                                  x.state != 'cancel'),
                         'Moves state is not cancel.')

    def test_finish_wizard_done(self):
        self.wiz = self.production_wiz.with_context(
            active_id=self.production.id).create(
                {'product_id': self.production.product_id.id,
                 'product_qty': 2,
                 })
        self.wiz.with_context(active_id=self.production.id).do_produce()
        move_lines = self.production.move_lines
        dest_move_lines = self.production.move_created_ids
        finish_wizard = self.production_finish_wiz.with_context(
            active_model='mrp.production',
            active_id=self.production.id).create({})
        finish_wizard.make_them_done()
        self.assertFalse(move_lines.filtered(lambda x: x.state != 'done'),
                         'Moves state is not done.')
        self.assertFalse(dest_move_lines.filtered(lambda x: x.state != 'done'),
                         'Moves state is not done.')
