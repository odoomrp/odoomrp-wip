# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestProcurementPlan(common.TransactionCase):
    def setUp(self):
        super(TestProcurementPlan, self).setUp()
        self.plan_model = self.env['procurement.plan']
        self.proc_model = self.env['procurement.order']
        self.wiz_sale_model = self.env['wiz.load.sale.from.plan']
        self.wiz_purchase_model = self.env['wiz.load.purchase.from.plan']
        self.wiz_proc_model = self.env['wiz.import.procurement.from.plan']
        self.wiz_date_model = self.env['wiz.change.procurement.date']
        vals = {'warehouse_id': self.env.ref('stock.warehouse0').id,
                'project_id': self.env.ref('project.project_project_1').id}
        self.plan = self.plan_model.create(vals)

    def test_procurement_plan_from_sales(self):
        self.plan.write(
            {'from_date': self.env.ref('sale.sale_order_7').date_order,
             'to_date': self.env.ref('sale.sale_order_7').date_order})
        vals = {'date_from': self.env.ref('sale.sale_order_7').date_order,
                'date_to': self.env.ref('sale.sale_order_7').date_order,
                'sale_id': self.env.ref('sale.sale_order_7').id,
                'partner_id': self.env.ref('sale.sale_order_7').partner_id.id}
        wiz_sale = self.wiz_sale_model.create(vals)
        wiz_sale.with_context(active_id=self.plan.id).load_sales()
        self.assertNotEqual(
            len(self.plan.procurement_ids), 0,
            'Have not been created procurements to the sales load from plan')
        self.assertEqual(
            len(self.plan.procurement_ids), self.plan.num_procurements,
            'Procurements the shortcut number does not match, in sales load'
            ' from plan')
        self.assertEqual(
            self.plan.state, 'running',
            'Procurement plan NOT in RUNNING state, after loading sales')
        self.plan.button_run()
        procurements = self.plan.procurement_ids.filtered(
            lambda x: x.state == 'confirmed')
        self.assertEqual(
            len(procurements), 0,
            'Found procurements in state CONFIRMED, after executing the plan')
        self.plan.button_cancel()
        procurements = self.plan.procurement_ids.filtered(
            lambda x: x.state == 'cancel')
        self.assertEqual(
            len(procurements), self.plan.num_procurements,
            'Not have canceled all procurements')
        self.plan.button_reset_to_confirm()
        procurements = self.plan.procurement_ids.filtered(
            lambda x: x.state == 'confirmed')
        self.assertEqual(
            len(procurements), self.plan.num_procurements,
            'Not have confirmed all procurements')
        self.plan.procurement_ids._compute_protect_date_planned()
        self.plan.procurement_ids.button_check()
        self.plan.procurement_ids[0].button_remove_plan()

    def test_procurement_plan_from_purchases(self):
        self.plan.write(
            {'from_date': self.env.ref('purchase.purchase_order_6').date_order,
             'to_date': self.env.ref('purchase.purchase_order_6').date_order})
        vals = {'date_from':
                self.env.ref('purchase.purchase_order_6').date_order,
                'date_to':
                self.env.ref('purchase.purchase_order_6').date_order,
                'purchase_id': self.env.ref('purchase.purchase_order_6').id,
                'partner_id':
                self.env.ref('purchase.purchase_order_6').partner_id.id}
        wiz_purchase = self.wiz_purchase_model.create(vals)
        wiz_purchase.with_context(active_id=self.plan.id).load_purchases()
        self.assertNotEqual(
            len(self.plan.procurement_ids), 0,
            'Have not been created procurements to the purchases load from'
            ' plan')
        self.assertEqual(
            len(self.plan.procurement_ids), self.plan.num_procurements,
            'Procurements the shortcut number does not match, in purchases'
            ' load from plan')
        self.assertEqual(
            self.plan.state, 'running',
            'Procurement plan NOT in RUNNING state, after loading purchases')
        self.plan.procurement_ids[0].cancel()
        self.assertEqual(
            self.plan.procurement_ids[0].state, 'cancel',
            'It has not been canceled the procurement')
        self.plan.procurement_ids[0].reset_to_confirmed()
        self.assertEqual(
            self.plan.procurement_ids[0].state, 'confirmed',
            'It has not been reset to confirm the procurement')
        self.plan.procurement_ids[0].button_run()
        self.assertNotEqual(
            self.plan.procurement_ids[0].state, 'confirmed',
            'Procurement in CONFIRMED state, before execute')

    def test_procurement_plan_from_procurements(self):
        cond = [('warehouse_id', '=', self.plan.warehouse_id.id),
                ('state', 'not in', ('cancel', 'done')),
                ('location_type', '=', 'internal'),
                ('plan', '=', False)]
        procurements = self.proc_model.search(cond)
        vals = {'warehouse_id': self.plan.warehouse_id.id,
                'procurement_ids': [(6, 0, procurements.ids)]}
        wiz_proc = self.wiz_proc_model.with_context(
            active_id=self.plan.id).create(vals)
        wiz_proc.with_context(active_id=self.plan.id).import_procurements()
        self.assertNotEqual(
            len(self.plan.procurement_ids), 0, 'Have not import procurements')
        self.assertEqual(
            len(self.plan.procurement_ids), self.plan.num_procurements,
            'Procurements the shortcut number does not match, in import'
            ' procurements')
        self.assertEqual(
            self.plan.state, 'running',
            'Procurement plan NOT in RUNNING state, after import procurements')

    def test_procurement_plan_change_procurement_date(self):
        cond = [('location_type', '=', 'internal')]
        procurements = self.proc_model.search(cond)
        procurements = procurements.filtered(
            lambda x: not x.purchase_line_id or (
                x.purchase_line_id and x.purchase_line_id.order_id.state ==
                'draft'))
        old_procurement_date = procurements[0].date_planned
        vals = {'old_scheduled_date': old_procurement_date,
                'procurements': [(6, 0, [procurements[0].id])],
                'days': 5}
        wiz_change_date = self.wiz_date_model.with_context(
            active_ids=[procurements[0].id]).create(vals)
        fields = ['old_scheduled_date', 'days', 'procurements']
        wiz_change_date.default_get(fields)
        wiz_change_date.change_scheduled_date()
        self.assertNotEqual(
            procurements[0].date_planned, old_procurement_date,
            'It has not changed the planned date of the procurement')
