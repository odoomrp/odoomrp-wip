# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class EditableScheduledProductTest(TransactionCase):

    def setUp(self):
        super(EditableScheduledProductTest, self).setUp()
        self.product_line_model = self.env['mrp.production.product.line']
        self.product = self.browse_ref('product.product_product_3')

    def test_line_onchange_product(self):
        line = self.product_line_model.new()
        line.product_id = self.product
        line._onchange_product_id()
        self.assertEqual(self.product.uom_id, line.product_uom,
                         'UoM should be equal.')
        self.assertEqual(self.product.name, line.name,
                         'Line name should be the product name.')
        try:
            self.assertEqual(
                self.product.product_tmpl_id, line.product_template,
                'If mrp_product_variants installed product template should be'
                ' product\'s template.')
        except:
            pass
