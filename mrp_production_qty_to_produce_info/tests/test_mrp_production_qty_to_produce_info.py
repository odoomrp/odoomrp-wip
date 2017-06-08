# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.tests.common as common
from openerp import workflow


class TestMrpProductionQtyToProduceInfo(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionQtyToProduceInfo, self).setUp()
        self.product_model = self.env['product.product']
        self.mrp_bom_model = self.env['mrp.bom']
        self.mrp_bom_line_model = self.env['mrp.bom.line']
        self.production_model = self.env['mrp.production']
        self.produce_model = self.env['mrp.product.produce']
        self.produce_line_model = self.env['mrp.product.produce.line']
        product_vals = {
            'name': 'Product to produce',
            'standard_price': 20.0,
            'list_price': 30.0,
            'type': 'product',
            'route_ids': [
                (6, 0,
                 [self.env.ref('mrp.route_warehouse0_manufacture').id,
                  self.env.ref('stock.route_warehouse0_mto').id])]}
        self.produce_product = self.product_model.create(product_vals)
        product_vals = {
            'name': 'Product to consume',
            'standard_price': 2.0,
            'list_price': 3.0,
            'type': 'product'}
        self.consume_product = self.product_model.create(product_vals)
        bom_vals = {'product_tmpl_id': self.produce_product.product_tmpl_id.id,
                    'product_id': self.produce_product.id}
        self.bom = self.mrp_bom_model.create(bom_vals)
        bom_line_vals = {'product_id': self.consume_product.id,
                         'bom_id': self.bom.id}
        self.mrp_bom_line_model.create(bom_line_vals)
        production_vals = {'product_id': self.produce_product.id,
                           'bom_id': self.bom.id,
                           'product_qty': 10,
                           'product_uom': self.produce_product.uom_id.id}
        self.production = self.production_model.create(production_vals)

    def test_confirm_production_and_produce(self):
        workflow.trg_validate(self.uid, 'mrp.production', self.production.id,
                              'button_confirm', self.cr)
        self.production.force_production()
        produce_vals = {'product_qty': 3,
                        'mode': 'consume_produce',
                        'product_id': self.produce_product.id,
                        'track_production': False}
        self.produce = self.produce_model.create(produce_vals)
        produce_line_vals = {'product_id': self.consume_product.id,
                             'product_qty': 3,
                             'produce_id': self.produce.id,
                             'track_production': False}
        self.produce_line_model.create(produce_line_vals)
        self.produce.with_context(active_id=self.production.id).do_produce()
        self.assertEqual(
            self.production.quantity_produced, 3, "Error in quantity produced")
        self.assertEqual(
            self.production.pending_quantity_to_produce, 7,
            "Error in pending quantity to produce")
