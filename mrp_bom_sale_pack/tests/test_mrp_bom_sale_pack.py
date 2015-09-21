# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp.tests import common


class TestMrpBomSalePack(common.TransactionCase):

    def setUp(self):
        super(TestMrpBomSalePack, self).setUp()
        self.product_model = self.env['product.product']
        self.partner1 = self.env.ref('base.res_partner_2')
        self.product_bom = self.product_model.create(
            {'name': 'Avanzosc'})
        self.product_bom1 = self.product_model.create(
            {'name': 'Pieza 1'})
        self.product_bom1.qty_available = 360.0
        self.product_bom2 = self.product_model.create(
            {'name': 'Pieza 2'})
        self.product_bom2.qty_available = 320.0
        self.mrp_bom_values = {
            'product_tmpl_id': self.product_bom.product_tmpl_id.id,
            'product_id': self.product_bom.id,
            'type': 'phantom'}
        self.mrp_bom_line1 = {
            'product_id': self.product_bom1.id,
            'product_qty': 3.0}
        self.mrp_bom_line2 = {
            'product_id': self.product_bom2.id,
            'product_qty': 2.0}
        self.mrp_bom_values['bom_line_ids'] = ([(0, 0, self.mrp_bom_line1),
                                                (0, 0, self.mrp_bom_line2)])
        self.mrp_bom_product = self.env['mrp.bom'].create(self.mrp_bom_values)
        self.sale_values = {
            'partner_id': self.partner1.id,
            'order_policy': 'manual'}
        self.line1_values = {
            'product_id': self.product_bom.id,
            'product_uom_qty': 2,
            'product_uom': self.product_bom.uom_id.id,
            'price_unit': 50,
        }

    def test_mrp_bom_stock(self):
        self.sale_order = self.env['sale.order'].create(self.sale_values)
        self.sale_order.order_line = [(0, 0, self.line1_values)]
        self.sale_order.action_button_confirm()
