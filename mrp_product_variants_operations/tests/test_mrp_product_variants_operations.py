# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestMrpProductVariantsOperations(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductVariantsOperations, self).setUp()
        self.production = self.env.ref(
            'mrp_operations_extension.mrp_production_opeext')

    def test_mrp_product_variants_operations(self):
        self.assertEqual(self.production.state, 'draft')
        self.production.signal_workflow('button_confirm')
        lines = self.production.product_lines.filtered(
            lambda x: not x.work_order or not x.product_id)
        self.assertEqual(
            len(lines), 0,
            'Scheduled goods without work order, or without product')
