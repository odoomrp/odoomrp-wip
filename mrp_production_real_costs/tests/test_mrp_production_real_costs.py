# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.tests.common as common
from openerp import workflow


class TestMrpProductionRealCosts(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionRealCosts, self).setUp()
        self.production_model = self.env['mrp.production']
        self.produce_model = self.env['mrp.product.produce']
        self.analytic_line_model = self.env['account.analytic.line']
        self.journal_materials = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_materials',
            False)
        self.journal_machines = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_machines',
            False)
        self.production = self.production_model.browse(
            self.env.ref('mrp_operations_extension.mrp_production_opeext').id)
        self.production_realcost = self.production.copy()

    def test_confirm_production_operation_real_costs(self):
        workflow.trg_validate(
            self.uid, 'mrp.production', self.production_realcost.id,
            'button_confirm', self.cr)
        self.production_realcost.force_production()
        vals_consume = []
        for line in self.production_realcost.move_lines:
            vals_consume.append((0, 0, {'product_id': line.product_id.id,
                                        'product_qty': line.product_uom_qty,
                                        'track_production': False}))
        produce_vals = {'product_qty': self.production_realcost.product_qty,
                        'mode': 'consume_produce',
                        'product_id': self.production_realcost.product_id.id,
                        'track_production': False,
                        'consume_lines': vals_consume}
        self.produce = self.produce_model.create(produce_vals)
        self.produce.with_context(
            active_id=self.production_realcost.id).do_produce()
        done_lines = self.production_realcost.move_created_ids2.filtered(
            lambda l: l.state == 'done')
        for line in done_lines:
            name = ('Final product - ' + (line.production_id.name or '') +
                    '-' + (line.product_id.default_code or ''))
            general_account = (
                line.product_id.property_account_income or
                line.product_id.categ_id.property_account_income_categ or
                self.property_model.get('property_account_expense_categ',
                                        'product.category'))
            cond = [('name', '=', name),
                    ('mrp_production_id', '=', line.production_id.id),
                    ('workorder', '=', False),
                    ('product_id', '=', line.product_id.id),
                    ('unit_amount', '=', line.product_qty),
                    ('account_id', '=',
                     self.production_realcost.analytic_account_id.id),
                    ('journal_id', '=', self.journal_materials.id),
                    ('general_account_id', '=', general_account.id)]
            analytic_lines = self.analytic_line_model.search(cond, limit=1)
            self.assertEqual(
                len(analytic_lines), 1,
                ('Analytic line not found for final product %s' %
                 (line.product_id.name)))
        for line in self.production_realcost.workcenter_lines:
            name = ((line.production_id.name or '') + '-' +
                    (line.routing_wc_line.operation.code or '') + '-' +
                    (line.workcenter_id.product_id.default_code or ''))
            general_acc = line.workcenter_id.costs_general_account_id or False
            operation_line = line.operation_time_lines[-1]
            journal = (line.workcenter_id.costs_journal_id or
                       self.journal_machines)
            cond = [('name', '=', name),
                    ('mrp_production_id', '=', line.production_id.id),
                    ('workorder', '=', line.id),
                    ('product_id', '=', line.workcenter_id.product_id.id),
                    ('unit_amount', '=', operation_line.uptime),
                    ('account_id', '=',
                     self.production_realcost.analytic_account_id.id),
                    ('journal_id', '=', journal.id),
                    ('general_account_id', '=', general_acc.id)]
            analytic_lines = self.analytic_line_model.search(cond, limit=1)
            self.assertEqual(
                len(analytic_lines), 1,
                ('Analytic line not found for workcenter line %s' %
                 (line.name)))
