# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestProcurementPlanMrp(common.TransactionCase):

    def setUp(self):
        super(TestProcurementPlanMrp, self).setUp()
        self.production_model = self.env['mrp.production']
        production_vals = {
            'product_id': self.env.ref('product.product_product_5').id,
            'product_qty': 1,
            'product_uom': 1}
        self.production = self.production_model.create(production_vals)
        self.sale_model = self.env['sale.order']
        self.plan_model = self.env['procurement.plan']
        vals = {'route_ids':
                [(6, 0,
                  [self.env.ref('stock.route_warehouse0_mto').id,
                   self.env.ref('mrp.route_warehouse0_manufacture').id])]}
        self.env.ref('product.product_product_19').write(vals)
        sale_vals = {
            'partner_id': self.env.ref('base.res_partner_2').id,
            'partner_shipping_id': self.env.ref('base.res_partner_2').id,
            'partner_invoice_id': self.env.ref('base.res_partner_2').id,
            'pricelist_id': self.env.ref('product.list0').id}
        product = self.env.ref('product.product_product_19')
        sale_line_vals = {
            'product_id': product.id,
            'name': product.name,
            'product_uos_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_procurement_plan_from_of(self):
        self.production.button_create_plan()
        self.assertNotEqual(
            self.production.plan, False, 'MRP production without plan')
        self.production.action_confirm()
        self.assertEqual(
            self.production.project_id.id, self.production.plan.project_id.id,
            'MRP production and plan with distinct project')

    def test_procurement_plan_mrp_create_from_sale_order(self):
        self.sale_order.company_id.proc_plan_level = 0
        self.sale_order.with_context(show_sale=True).action_button_confirm()
        cond = [('name', 'ilike', self.sale_order.name)]
        plan = self.plan_model.search(cond)
        self.assertNotEqual(
            len(plan), 0, 'It has not generated the PROCUREMENT PLAN,'
                          ' confirming the sales order')
        procurements = plan.procurement_ids.filtered(
            lambda x: x.level >= 0 and
            x.level <= x.company_id.proc_plan_level and
            x.state == 'running')
        self.assertNotEqual(
            len(procurements), 0,
            'Procurement orders with level not confirmed, confirming the sales'
            ' order')
