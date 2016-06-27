# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields


class TestStockQuantValuation(common.TransactionCase):

    def setUp(self):
        super(TestStockQuantValuation, self).setUp()
        self.quant_model = self.env['stock.quant']
        self.hist_model = self.env['stock.history']
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

    def test_stock_history(self):
        hist_line = self.hist_model.search([], limit=1)
        hist_line.product_id.sudo().manual_standard_cost = 40
        self.assertEqual(hist_line.manual_value, (hist_line.quantity * 40),
                         "Incorrect Manual Value for history line.")
        self.assertEqual(hist_line.real_value,
                         (hist_line.quantity * hist_line.price_unit_on_quant),
                         "Incorrect Real Value for history line.")

    def test_stock_history_read_group(self):
        gfields = ['product_id', 'location_id', 'move_id', 'date', 'source',
                   'quantity', 'inventory_value', 'manual_value', 'real_value']
        groupby = ['product_id']
        domain = [('date', '<=', fields.Date.today())]
        res = self.hist_model.read_group(
            domain=domain, fields=gfields, groupby=groupby, offset=0,
            limit=None, orderby=False, lazy=True)
        if res:
            line = res[0]
            line_domain = line.get('__domain', domain)
            group_lines = self.hist_model.search(line_domain)
            sum_real = sum([x.real_value for x in group_lines])
            sum_manual = sum([x.manual_value for x in group_lines])
            self.assertEqual(line['real_value'], sum_real,
                             "Real value not correct sum.")
            self.assertEqual(line['manual_value'], sum_manual,
                             "Manual value not correct sum.")
