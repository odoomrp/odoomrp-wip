# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestMrpBomThroughAttribute(common.TransactionCase):
    def setUp(self):
        super(TestMrpBomThroughAttribute, self).setUp()
        self.raw_material = self.env['product.product'].create(
            {'name': 'Test raw material'})
        self.attribute = self.env['product.attribute'].create(
            {'name': 'Component'})
        self.value = self.env['product.attribute.value'].create(
            {'name': 'Raw material',
             'attribute_id': self.attribute.id,
             'raw_product': self.raw_material.id,
             'raw_qty': 2.0})
        self.final_template = self.env['product.template'].create(
            {
                'name': 'Test final product with attributes',
                'attribute_line_ids': [
                    (0, 0, {
                        'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, self.value.ids)]})]
            })
        self.final_product = self.final_template.product_variant_ids[0]
        self.bom = self.env['mrp.bom'].create(
            {
                'product_id': self.final_product.id,
                'product_tmpl_id': self.final_template.id,
            })

    def test_production_with_component_through_attributes(self):
        production = self.env['mrp.production'].create(
            {
                'product_id': self.final_product.id,
                'product_uom': self.final_product.uom_id.id,
                'bom_id': self.bom.id,
                'product_qty': 3.0,
            })
        production.action_compute()
        self.assertEqual(len(production.product_lines), 1)
        self.assertEqual(production.product_lines[0].product_qty, 6.0)
