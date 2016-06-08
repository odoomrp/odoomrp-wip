# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Javier Iniesta
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from openerp.tests.common import TransactionCase
from openerp.addons.product_variant_cost_price.tests.\
    test_product_product import TestProductProduct


class TestProductPriceHistory(TestProductProduct):

    def setUp(self):
        super(TestProductPriceHistory, self).setUp()
        self.variant_history_model = self.env['product.price.history.product']
        self.tmpl_history_model = self.env['product.price.history']

    def test_product_single_read_last_cost(self):
        self.product_single.standard_price = 100
        history = self.variant_history_model.search(
            [('product_id', '=', self.product_single.id)])
        self.assertEqual(self.product_single.standard_price, 100)
        self.assertEqual(self.product_single.standard_price, history[:1].cost)
        self.assertEqual(history[:1].cost, 100)
        history = self.tmpl_history_model.search(
            [('product_template_id', '=', self.template_single.id)])
        self.assertEqual(self.template_single.standard_price, 100)
        self.assertEqual(self.template_single.standard_price, history[:1].cost)
        self.assertEqual(history[:1].cost, 100)

    def test_product_multi_read_last_cost(self):
        history = self.variant_history_model.search(
            [('product_id', '=', self.product_multi_1.id)])
        self.assertEqual(self.product_multi_1.standard_price, history[:1].cost)
        history = self.tmpl_history_model.search(
            [('product_template_id', '=', self.template_multi.id)])
        self.assertEqual(self.template_multi.standard_price, history[:1].cost)
