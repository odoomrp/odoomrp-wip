# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestAllowedProduct(common.TransactionCase):

    def setUp(self):
        super(TestAllowedProduct, self).setUp()
        self.sale_model = self.env['sale.order']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'customer': True,
        })
        product_model = self.env['product.product']
        self.product1 = product_model.create({
            'name': 'Test Product 1',
            'sale_ok': True,
        })
        self.product2 = product_model.create({
            'name': 'Test Product 2',
            'sale_ok': True,
        })
        self.env['product.supplierinfo'].create({
            'name': self.partner.id,
            'product_tmpl_id': self.product1.product_tmpl_id.id,
            'type': 'customer',
        })

    def test_sale_allowed_product(self):
        sale_order = self.sale_model.create({
            'partner_id': self.partner.id,
            'only_allowed_products': True,
        })
        self.assertIn(
            self.product1.product_tmpl_id, sale_order.allowed_tmpl_ids)
        self.assertIn(self.product1, sale_order.allowed_product_ids)
        self.assertNotIn(
            self.product2.product_tmpl_id, sale_order.allowed_tmpl_ids)
        self.assertNotIn(self.product2, sale_order.allowed_product_ids)
