# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.product_variants_no_automatic_creation.tests.\
    test_product_variants import (TestProductVariant)


class TestMrpProductVariants(TestProductVariant):

    def setUp(self):
        super(TestMrpProductVariants, self).setUp()
        self.bom_model = self.env['mrp.bom']
        self.production_model = self.env['mrp.production']
        self.template = self.tmpl_model.create({
            'name': 'Category option template',
            'categ_id': self.categ2.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.variant = self.template.product_variant_ids[:1]
        bom = self.bom_model.create({
            'name': 'Variant Template BoM',
            'product_tmpl_id': self.template.id,
            'product_qty': 1.0,
            'product_uom': self.template.uom_id.id,
            'type': 'normal'
        })
        self.production = self.production_model.create({
            'product_tmpl_id': self.template.id,
            'product_qty': 50.0,
            'product_uom': self.template.uom_id.id,
            'bom_id': bom.id
        })

    def test_load_attribute_lines_in_onchange(self):
        self.production.product_id = self.variant
        res = self.production.product_id_change(self.variant.id, 50)
        self.assertTrue(res['value'].get('product_attribute_ids', False),
                        'Not attributes loaded')
