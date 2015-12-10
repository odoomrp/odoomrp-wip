# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestStockInvoicingType(common.TransactionCase):

    def setUp(self):
        super(TestStockInvoicingType, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.procurement_model = self.env['procurement.order']
        self.product = self.browse_ref('product.product_product_3')
        self.sale_order = self.sale_order_model.create({
            'partner_id': self.ref('base.res_partner_2'),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
            })],
        })

    def test_procurement_run(self):
        self.sale_order.action_button_confirm()
        procurement = self.procurement_model.search(
            [('origin', '=', self.sale_order.name),
             ('product_id', '=', self.product.id)])
        self.assertEqual(
            len(procurement), 1, "Procurement not generated for product.")
        procurement.run()
        for picking in procurement.mapped('move_ids.picking_id'):
            self.assertEqual(
                picking.invoice_type_id, self.sale_order.invoice_type_id,
                "Sale order and Picking must have the same invoice type.")
