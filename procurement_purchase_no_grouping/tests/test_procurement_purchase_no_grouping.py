# -*- coding: utf-8 -*-
# Copyright 2015-2016 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp.tests.common import TransactionCase


class TestProcurementPurchaseNoGrouping(TransactionCase):

    def setUp(self):
        super(TestProcurementPurchaseNoGrouping, self).setUp()
        self.category = self.env['product.category'].create({
            'name': 'Test category',
        })
        self.product = self.env['product.product'].create({
            'name': 'Test product',
            'categ_id': self.category.id,
            'seller_ids': [
                (0, 0, {
                    'name': self.env.ref('base.res_partner_1').id,
                    'min_qty': 1.0,
                }),
            ]}
        )
        self.procurement = self.env['procurement.order'].create({
            'name': 'Procurement test',
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (6, 0, [self.env.ref('purchase.route_warehouse0_buy').id]),
            ],
            'product_qty': 1.0,
        }
        )

    def test_procurement_grouped_purchase(self):
        self.category.procured_purchase_grouping = 'standard'
        procurement_1 = self.procurement.copy()
        procurement_2 = self.procurement.copy()
        procurement_1.run()
        procurement_2.run()
        self.assertTrue(procurement_1.purchase_id)
        self.assertTrue(procurement_2.purchase_id)
        self.assertEqual(
            procurement_1.purchase_id, procurement_2.purchase_id,
            'Procured purchase orders are not the same',
        )
        self.assertEqual(
            procurement_1.purchase_line_id, procurement_2.purchase_line_id,
            'Procured purchase orders lines are not the same',
        )
        return True

    def test_procurement_no_grouping_line_purchase(self):
        self.category.procured_purchase_grouping = 'line'
        procurement_1 = self.procurement.copy()
        procurement_2 = self.procurement.copy()
        procurement_1.run()
        procurement_2.run()
        self.assertTrue(procurement_1.purchase_id)
        self.assertTrue(procurement_2.purchase_id)
        self.assertEqual(
            procurement_1.purchase_id, procurement_2.purchase_id,
            'Procured purchase orders are not the same',
        )
        self.assertNotEqual(
            procurement_1.purchase_line_id, procurement_2.purchase_line_id,
            'Procured purchase orders lines are the same',
        )
        return True

    def test_procurement_no_grouping_order_purchase(self):
        self.category.procured_purchase_grouping = 'order'
        procurement_1 = self.procurement.copy()
        procurement_2 = self.procurement.copy()
        procurement_1.run()
        procurement_2.run()
        self.assertTrue(procurement_1.purchase_id)
        self.assertTrue(procurement_2.purchase_id)
        self.assertNotEqual(
            procurement_1.purchase_id, procurement_2.purchase_id,
            'Procured purchase orders are the same',
        )
        self.assertNotEqual(
            procurement_1.purchase_line_id, procurement_2.purchase_line_id,
            'Procured purchase orders lines are the same',
        )
        return True
