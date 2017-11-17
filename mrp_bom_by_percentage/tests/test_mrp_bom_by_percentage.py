# -*- coding: utf-8 -*-
# (Copyright) 2017 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


import openerp.tests.common as common
from openerp import exceptions


class TestMrpBomByPercentage(common.TransactionCase):

    def setUp(self):
        super(TestMrpBomByPercentage, self).setUp()
        self.bom = self.env.ref('mrp.mrp_bom_11')
        self.product = self.ref('product.product_product_5b')

    def test_mrp_bom_by_percentage(self):
        self.assertEqual(self.bom.qty_to_consume,
                         sum(self.bom.mapped('bom_line_ids.product_qty')))
        with self.assertRaises(exceptions.ValidationError):
            self.bom.by_percentage = True
        qty = 100 - self.bom.qty_to_consume
        bom_line = {
            'product_id': self.product,
            'type': 'normal',
            'product_qty': qty,
            'product_efficiency': 1.0,
        }
        self.bom.bom_line_ids = [(0, 0, bom_line)]
        self.assertEqual(self.bom.qty_to_consume, 100,
                         'Qty to consume should be 100')
        self.bom.by_percentage = True
        self.bom.onchange_by_percentage()
        self.assertEqual(self.bom.product_qty, 100,
                         'Product qty should be 100')
