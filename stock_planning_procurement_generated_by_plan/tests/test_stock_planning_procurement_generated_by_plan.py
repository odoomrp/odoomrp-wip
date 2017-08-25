# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta


class TestStockPlanningProcurementGeneratedByPlan(common.TransactionCase):

    def setUp(self):
        super(TestStockPlanningProcurementGeneratedByPlan, self).setUp()
        self.sale_model = self.env['sale.order']
        self.plan_model = self.env['procurement.plan']
        self.procurement_model = self.env['procurement.order']
        self.reservation_model = self.env['stock.reservation']
        self.wizard_model = self.env['wiz.stock.planning']
        self.planning_model = self.env['stock.planning']
        self.mrp_route = self.env.ref('mrp.route_warehouse0_manufacture')
        vals = {'route_ids':
                [(6, 0,
                  [self.env.ref('stock.route_warehouse0_mto').id,
                   self.mrp_route.id])]}
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

    def test_stock_planning_procurement_generated_by_plan(self):
        self.sale_order.with_context(show_sale=True).action_button_confirm()
        cond = [('name', 'ilike', self.sale_order.name)]
        plan = self.plan_model.search(cond)
        self.assertNotEqual(
            len(plan), 0, 'It has not generated the PROCUREMENT PLAN,'
                          ' confirming the sales order')
        for procurement in plan.procurement_ids.filtered(
                lambda r: r.level == 0 and
                r.location_id.usage == 'internal' and
                self.mrp_route.id in r.product_id.route_ids.ids):
            cond = [('parent_procurement_id', '=', procurement.id)]
            child_procs = self.env['procurement.order'].search(cond)
            child_procs.cancel()
            child_procs.unlink()
        plan.button_generate_mrp_procurements()
        procurement = plan.procurement_ids[1]
        to_date = fields.Date.to_string(
            fields.Date.from_string(procurement.date_planned) +
            relativedelta(days=30))
        wiz_vals = {'company': procurement.company_id.id,
                    'days': 7,
                    'to_date': to_date,
                    'product': procurement.product_id.id}
        wizard = self.wizard_model.create(wiz_vals)
        wizard.calculate_stock_planning()
        cond = [('product', '=', procurement.product_id.id)]
        plannings = self.planning_model.search(cond)
        self.assertNotEqual(
            len(plannings), 0, 'It has not generated the STOCK PLANNING')
