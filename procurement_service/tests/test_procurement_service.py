# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.tests.common as common


class TestProcurementService(common.TransactionCase):

    def setUp(self):
        super(TestProcurementService, self).setUp()
        self.product_model = self.env['product.product']
        self.route_model = self.env['stock.location.route']
        self.sale_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.procurement_model = self.env['procurement.order']
        routes = self.route_model.search(
            [('name', 'in', ('Make To Order', 'Buy'))])
        self.assertEqual(len(routes), 2,
                         "Make to order, and buy routes not found")
        vals = {'name': 'Service Generated Procurement',
                'standard_price': 20.5,
                'list_price': 30.75,
                'type': 'service',
                'route_ids': [(6, 0, routes.mapped('id'))],
                }
        self.new_service_product = self.product_model.create(vals)
        vals = self.sale_model.onchange_partner_id(
            self.env.ref('base.res_partner_1').id).get('value')
        vals['partner_id'] = self.env.ref('base.res_partner_1').id
        line = self.sale_line_model.product_id_change(
            pricelist=vals.get('pricelist_id'),
            product=self.new_service_product.id, qty=1, qty_uos=1,
            partner_id=self.env.ref('base.res_partner_1').id).get('value')
        line['product_id'] = self.new_service_product.id
        vals['order_line'] = [(0, 0, line)]
        self.new_sale_order = self.sale_model.create(vals)

    def test_confirm_sale_and_generate_procurement_service(self):
        self.new_sale_order.action_button_confirm()
        for line in self.new_sale_order.order_line:
            cond = [('sale_line_id', '=', line.id)]
            procs = self.procurement_model.search(cond)
            self.assertEqual(
                len(procs), 1,
                "Procurement not generated for the service product type")
