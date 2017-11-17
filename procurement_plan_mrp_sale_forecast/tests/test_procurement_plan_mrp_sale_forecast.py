# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestProcurementPlanMrpSaleForecast(common.TransactionCase):

    def setUp(self):
        super(TestProcurementPlanMrpSaleForecast, self).setUp()
        self.sale_forecast_model = self.env['procurement.sale.forecast']
        self.wiz_model = self.env['make.procurement']
        forecast_vals = {
            'name': 'Procurement plan mrp sale forecast test',
            'date_from': '2025-01-01',
            'date_to': '2025-01-31',
            'warehouse_id': self.ref('stock.stock_warehouse_shop0'),
            'forecast_lines': [
                (0, 0, {'partner_id': self.ref('base.res_partner_address_2'),
                        'date': '2025-01-15',
                        'product_id': self.ref('product.product_product_4b'),
                        'qty': 1,
                        'unit_price': 5}),
                (0, 0, {'partner_id': self.ref('base.res_partner_address_2'),
                        'date': '2025-01-20',
                        'product_id': self.ref('product.product_product_4c'),
                        'qty': 4,
                        'unit_price': 12})]}
        self.sale_forecast = self.sale_forecast_model.create(forecast_vals)

    def test_procurement_plan_mrp_sale_forecast(self):
        line = self.sale_forecast.forecast_lines[0]
        wiz_vals = {'warehouse_id': self.ref('stock.stock_warehouse_shop0'),
                    'product_id': self.ref('product.product_product_4b'),
                    'uom_id':
                    self.env.ref('product.product_product_4b').uom_id.id,
                    'qty': 1,
                    'date_planned': '2025-01-15'}
        wiz = self.wiz_model.create(wiz_vals)
        wiz.with_context({'active_model': 'procurement.sale.forecast.line',
                          'active_ids': [line.id],
                          'active_id': line.id}).make_procurement()
        self.assertNotEqual(
            self.sale_forecast.forecast_lines[0].procurement_id, False,
            'Line without procurement')
        self.sale_forecast.create_procurements()
        for line in self.sale_forecast.forecast_lines:
            self.assertNotEqual(line.procurement_id, False,
                                'Case 2, line without procurement')
