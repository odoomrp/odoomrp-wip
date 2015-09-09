# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.tests.common as common
from openerp import workflow, _


class TestMrpProductionProjectEstimatedCost(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionProjectEstimatedCost, self).setUp()
        self.production_model = self.env['mrp.production']
        self.property_model = self.env['ir.property']
        self.analytic_line_model = self.env['account.analytic.line']
        self.production = self.production_model.browse(
            self.env.ref('mrp_operations_extension.mrp_production_opeext').id)
        self.production_estimcost = self.production.copy()
        self.journal_materials = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_materials',
            False)
        self.journal_machines = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_machines',
            False)
        self.journal_operators = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_operators',
            False)

    def test_confirm_production_operation_estimated_cost(self):
        workflow.trg_validate(
            self.uid, 'mrp.production', self.production_estimcost.id,
            'button_confirm', self.cr)
        for line in self.production_estimcost.product_lines:
            name = _('%s-%s' % (self.production_estimcost.name,
                                line.work_order.name or ''))
            general_account = (
                line.product_id.property_account_income or
                line.product_id.categ_id.property_account_income_categ or
                self.property_model.get('property_account_expense_categ',
                                        'product.category'))
            cond = [('name', '=', name),
                    ('mrp_production_id', '=', self.production_estimcost.id),
                    ('workorder', '=', (line.work_order and line.work_order.id
                                        or False)),
                    ('product_id', '=', (line.product_id and line.product_id.id
                                         or False)),
                    ('unit_amount', '=', line.product_qty),
                    ('account_id', '=',
                     self.production_estimcost.analytic_account_id.id),
                    ('journal_id', '=', self.journal_materials.id),
                    ('general_account_id', '=', general_account.id)]
            analytic_lines = self.analytic_line_model.search(cond, limit=1)
            self.assertEqual(
                len(analytic_lines), 1,
                ('Analytic line not found for material %s' %
                 (line.product_id.name)))
        for line in self.production_estimcost.workcenter_lines:
            op_wc_lines = line.routing_wc_line.op_wc_lines
            wc = op_wc_lines.filtered(lambda r: r.workcenter ==
                                      line.workcenter_id) or line.workcenter_id
            product = line.workcenter_id.product_id
            name = (_('%s-%s-C-%s') %
                    (self.production_estimcost.name,
                     line.routing_wc_line.operation.code,
                     line.workcenter_id.name))
            general_account = (
                product.property_account_income or
                product.categ_id.property_account_income_categ or
                self.property_model.get('property_account_expense_categ',
                                        'product.category'))
            cond = [('name', '=', name),
                    ('mrp_production_id', '=',
                     self.production_estimcost.id),
                    ('workorder', '=', line and line.id or False),
                    ('product_id', '=', product and product.id or False),
                    ('unit_amount', '=', line.cycle),
                    ('account_id', '=',
                     self.production_estimcost.analytic_account_id.id),
                    ('journal_id', '=', self.journal_machines.id),
                    ('general_account_id', '=', general_account.id)]
            analytic_lines = self.analytic_line_model.search(cond, limit=1)
            self.assertEqual(
                len(analytic_lines), 1,
                ('Analytic line not found for cycle product %s' %
                 (product.name)))
            product = line.workcenter_id.product_id
            name = (_('%s-%s-%s') %
                    (self.production_estimcost.name,
                     line.routing_wc_line.operation.code, product.name))
            general_account = (
                product.property_account_income or
                product.categ_id.property_account_income_categ or
                self.property_model.get(
                    'property_account_expense_categ',
                    'product.category'))
            cond = [('name', '=', name),
                    ('mrp_production_id', '=',
                     self.production_estimcost.id),
                    ('workorder', '=', line and line.id or False),
                    ('product_id', '=', product and product.id or False),
                    ('unit_amount', '=', line.hour * wc.op_number),
                    ('account_id', '=',
                     self.production_estimcost.analytic_account_id.id),
                    ('journal_id', '=', self.journal_operators.id),
                    ('general_account_id', '=', general_account.id)]
            analytic_lines = self.analytic_line_model.search(cond,
                                                             limit=1)
            self.assertEqual(
                len(analytic_lines), 1,
                ('Analytic line not found for operator product %s' %
                 (product.name)))
