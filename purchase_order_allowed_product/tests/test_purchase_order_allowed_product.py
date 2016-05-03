# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestAllowedProduct(common.TransactionCase):

    def setUp(self):
        super(TestAllowedProduct, self).setUp()
        self.purchase_model = self.env['purchase.order']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'supplier': True,
        })
        product_model = self.env['product.product']
        self.product1 = product_model.create({
            'name': 'Test Product 1',
            'purchase_ok': True,
        })
        self.product2 = product_model.create({
            'name': 'Test Product 2',
            'purchase_ok': True,
        })
        self.env['product.supplierinfo'].create({
            'name': self.partner.id,
            'product_tmpl_id': self.product1.product_tmpl_id.id,
        })

    def test_purchase_allowed_product(self):
        purchase_order = self.purchase_model.create({
            'partner_id': self.partner.id,
            'pricelist_id': self.ref('purchase.list0'),
            'only_allowed_products': True,
            'location_id': self.ref('stock.stock_location_stock'),
        })
        self.assertIn(
            self.product1.product_tmpl_id, purchase_order.allowed_tmpl_ids)
        self.assertIn(self.product1, purchase_order.allowed_product_ids)
        self.assertNotIn(
            self.product2.product_tmpl_id, purchase_order.allowed_tmpl_ids)
        self.assertNotIn(self.product2, purchase_order.allowed_product_ids)
