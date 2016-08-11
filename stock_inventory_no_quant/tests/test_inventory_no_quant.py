# -*- coding: utf-8 -*-
# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestInventoryNoQuant(common.TransactionCase):

    def setUp(self):
        super(TestInventoryNoQuant, self).setUp()
        self.inventory = self.env['stock.inventory'].create({
            'name': 'Inventory Test',
            'filter': 'none'})

    def test_inventory_none(self):
        self.inventory.prepare_inventory()
        all_products = self.env['product.product'].search([
            ('type', '=', 'product')])
        self.assertEqual(len(self.inventory.line_ids), len(all_products))

    def test_inventory_product(self):
        # Select product with no quants
        self.inventory.write({
            'filter': 'product',
            'product_id': self.ref('product.product_product_8'),
        })
        self.inventory.prepare_inventory()
        self.assertEqual(len(self.inventory.line_ids), 1)
