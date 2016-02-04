# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestStockQuantNameSearch(common.TransactionCase):
    def setUp(self):
        super(TestStockQuantNameSearch, self).setUp()
        self.lot_name = 'StockQuantTestLot'
        self.product_name = 'StockQuantTestProduct'
        self.uom = self.browse_ref('product.product_uom_dozen')
        self.quant_model = self.env['stock.quant'].sudo()
        product = self.env['product.product'].create({
            'name': self.product_name,
            'uom_id': self.uom.id,
        })
        lot_id = self.env['stock.production.lot'].create({
            'name': self.lot_name,
            'product_id': product.id,
        })
        location_id = self.ref('stock.stock_location_customers')
        self.quant1 = self.quant_model.create({
            'product_id': product.id,
            'lot_id': lot_id.id,
            'qty': 10.0,
            'location_id': location_id,
        })
        self.quant2 = self.quant_model.create({
            'product_id': product.id,
            'qty': 10.0,
            'location_id': location_id,
        })
        self.quant3 = self.quant_model.create({
            'product_id': self.ref('product.product_product_3'),
            'qty': 10.0,
            'location_id': location_id,
        })

    def test_quant_name_search_lot(self):
        res_search = self.quant_model.name_search(name=self.lot_name)
        quant_ids = map(lambda x: x[0], res_search)
        self.assertNotEqual(
            len(res_search), 0, 'There must be at least one quant created.')
        self.assertEqual(
            len(res_search), 1, 'There must be only one quant created.')
        self.assertIn(self.quant1.id, quant_ids)
        self.assertNotIn(self.quant2.id, quant_ids)
        self.assertNotIn(self.quant3.id, quant_ids)

    def test_quant_name_search_product(self):
        res_search = self.quant_model.name_search(name=self.product_name)
        quant_ids = map(lambda x: x[0], res_search)
        self.assertNotEqual(
            len(res_search), 0, 'There must be at least one quants created.')
        self.assertEqual(
            len(res_search), 2, 'There must be only two quants created.')
        self.assertIn(self.quant1.id, quant_ids)
        self.assertIn(self.quant2.id, quant_ids)
        self.assertNotIn(self.quant3.id, quant_ids)

    def test_quant_name_search_uom(self):
        res_search = self.quant_model.name_search(name=self.uom.name)
        quant_ids = map(lambda x: x[0], res_search)
        self.assertNotEqual(
            len(res_search), 0, 'There must be at least one quants created.')
        self.assertTrue(
            len(res_search) >= 2, 'There must be at least two quants created.')
        self.assertIn(self.quant1.id, quant_ids)
        self.assertIn(self.quant2.id, quant_ids)
        self.assertNotIn(self.quant3.id, quant_ids)
