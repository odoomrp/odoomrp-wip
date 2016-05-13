# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestStockQuantValuation(common.TransactionCase):

    def setUp(self):
        super(TestStockQuantValuation, self).setUp()
        self.quant_model = self.env['stock.quant']
        self.location_model = self.env['stock.location']
        self.product = self.env.ref('product.product_product_34')
        self.location = self.location_model.search([('usage', '=',
                                                     'internal')], limit=1)

    def test_quant_valuation(self):
        self.product.sudo().write({'cost_method': 'real',
                                   'standard_price': 20,
                                   'manual_standard_cost': 35})
        quant = self.quant_model.create(
            {'product_id': self.product.id,
             'cost': 20,
             'location_id': self.location.id,
             'qty': 5})
        self.assertEqual(quant.manual_value, (35 * 5),
                         "Incorrect Manual Value for quant.")
        self.assertEqual(quant.real_value, (20 * 5),
                         "Incorrect Real Value for quant.")
