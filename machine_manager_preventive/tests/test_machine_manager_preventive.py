# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common
from openerp.exceptions import ValidationError, Warning as UserError


class TestMachineManagerPreventive(common.TransactionCase):

    def setUp(self):
        super(TestMachineManagerPreventive, self).setUp()
        self.machine_1 = self.env.ref('machine_manager.machinery_1')
        self.machine_2 = self.env.ref('machine_manager_preventive.machinery_2')
        self.preventive_master = self.env.ref(
            'machine_manager_preventive.preventive_master_1')
        self.preventive_tmpl_1 = self.env.ref(
            'machine_manager_preventive.preventive_operation_type_1')
        self.op_material_1 = self.env.ref(
            'machine_manager_preventive.preventive_operation_material_1')
        self.op_matmatch_1 = self.env.ref(
            'machine_manager_preventive.preventive_operation_matmatch_1')
        self.preventive_op1 = self.env.ref(
            'machine_manager_preventive.preventive_machine_operation_1')
        self.preventive_op2 = self.env.ref(
            'machine_manager_preventive.preventive_machine_operation_2')
        self.preventive_op3 = self.env.ref(
            'machine_manager_preventive.preventive_machine_operation_3')
        self.wiz_model = self.env['preventive.create.wizard']
        self.wiz_prev_list_model = self.env['preventive.list']
        self.prev_machine_op_obj = self.env['preventive.machine.operation']
        self.repair_wiz_model = self.env['preventive.repair.order']
        self.repair_obj = self.env['mrp.repair']
        self.repair_line_obj = self.env['mrp.repair.line']

    def test_check_basedoncy(self):
        with self.assertRaises(ValidationError):
            # No cycles number defined
            self.preventive_tmpl_1.cycles = 0

    def test_check_basedontime(self):
        with self.assertRaises(ValidationError):
            # No frequency number defined
            self.preventive_tmpl_1.frequency = 0

    def test_onchange_interval_unit(self):
        pre_interval_unit1 = self.preventive_tmpl_1.interval_unit1
        self.preventive_tmpl_1.interval_unit = 'week'
        self.preventive_tmpl_1._onchange_interval_unit()
        self.assertNotEqual(pre_interval_unit1,
                            self.preventive_tmpl_1.interval_unit1,
                            'Error in onchange')

    def test_check_tmpl_cycle_margins(self):
        with self.assertRaises(ValidationError):
            # margin_cy1 < margin_cy2
            self.preventive_tmpl_1.margin_cy1 = self.preventive_tmpl_1.\
                margin_cy2 + 1

    def test_check_tmpl_time_margins(self):
        with self.assertRaises(ValidationError):
            # margin_cy1 < margin_cy2
            self.preventive_tmpl_1.interval_unit1 = self.preventive_tmpl_1.\
                interval_unit2
            self.preventive_tmpl_1.margin_fre1 = self.preventive_tmpl_1.\
                margin_fre2 + 1

    def test_onchange_product(self):
        pre_uom = self.op_material_1.product_uom.id
        new_product = self.env.ref(
            'machine_manager_preventive.product_product_clean_spray')
        self.op_material_1.product_id = new_product
        self.op_material_1._onchange_product()
        self.assertNotEqual(pre_uom, self.op_material_1.product_uom.id,
                            'Error in onchange')

    def test_onchange_optype_id(self):
        self.preventive_tmpl_1.description = 'New description'
        self.op_matmatch_1._onchange_optype_id()
        self.assertEqual('New description', self.op_matmatch_1.description,
                         'Error in onchange')

    def test_check_cycle_margins(self):
        with self.assertRaises(ValidationError):
            # first_margin < second_margin
            self.preventive_op1.first_margin = self.preventive_op1.\
                second_margin + 1

    def test_check_time_margins(self):
        with self.assertRaises(ValidationError):
            # first_margin < second_margin
            self.preventive_op1.margin_fre1 = self.preventive_op1.\
                margin_fre2 + 1

    def test_check_alert_by_cycles(self):
        pre_state_alert = self.preventive_op1.alert
        self.preventive_op1._onchange_cycles_alert()
        self.assertEqual(pre_state_alert, self.preventive_op1.alert,
                         'Error in onchange_cycles_alert')
        self.machine_1.actcycles = 240
        self.preventive_op1._onchange_cycles_alert()
        self.assertNotEqual(pre_state_alert, self.preventive_op1.alert,
                            'Error in onchange_cycles_alert')
        pre_state_al1 = self.preventive_op1.check_al1
        pre_state_al2 = self.preventive_op1.check_al2
        self.preventive_op1.set_alarm1()
        self.preventive_op1.set_alarm2()
        self.assertNotEqual(pre_state_al1, self.preventive_op1.check_al1,
                            'Error in set')
        self.assertNotEqual(pre_state_al2, self.preventive_op1.check_al2,
                            'Error in set')

    def test_check_alert_by_time(self):
        pre_state_alert = self.preventive_op1.alert
        pre_state_extra_alert = self.preventive_op1.extra_alert
        self.preventive_op1.lastdate = '2016-01-01'
        self.preventive_op1.check_alerts()
        self.assertNotEqual(pre_state_alert, self.preventive_op1.alert,
                            'Error in check_alerts')
        self.assertNotEqual(pre_state_extra_alert,
                            self.preventive_op1.extra_alert,
                            'Error in check_alerts')

    def test_show_attachments(self):
        res = self.preventive_op1.show_attachments()
        self.assertIsNotNone(res, 'Error in show_attachments')

    def test_create_preventive_wizard(self):
        pre_prevent_ops = len(self.prev_machine_op_obj.search([]))
        wiz_res = self.wiz_model.with_context(
            active_ids=[self.preventive_master.id]).create_preventive()
        post_prevent_ops = len(self.prev_machine_op_obj.search([]))
        self.assertNotEqual(pre_prevent_ops, post_prevent_ops,
                            'Error in pre_wiz')
        data_res = self.wiz_prev_list_model.with_context(
            wiz_res['context']).create({})
        self.assertEqual(data_res['op_count'], 1, 'Error in preventive list')

    def test_create_repair_order(self):
        pre_repairs = len(self.repair_obj.search(
            [('idmachine', '=', self.machine_1.id),
             ('state', 'in', ('draft', 'confirmed', 'ready'))]))
        wizard = self.repair_wiz_model.with_context(
            active_ids=[self.preventive_op1.id,
                        self.preventive_op3.id]).create({})
        with self.assertRaises(UserError):
            # No product multiple call
            product = self.preventive_op3.machine.product
            self.preventive_op3.machine.product = False
            wizard.create_repair_from_pmo()
        self.preventive_op3.machine.product = product
        repair_ids = wizard.create_repair_from_pmo()['domain'][0][2]
        post_repairs = len(self.repair_obj.search(
            [('idmachine', '=', self.machine_1.id),
             ('state', 'in', ('draft', 'confirmed', 'ready'))]))
        self.assertNotEqual(pre_repairs, post_repairs, 'Error in repair_wiz')
        with self.assertRaises(UserError):
            # view not updated
            self.preventive_op2.active_repair_order = False
            self.preventive_op2.create_repair_order()
        self.preventive_op2.active_repair_order = True
        product2 = self.preventive_op2.machine.product
        with self.assertRaises(UserError):
            # No product simple call
            self.preventive_op2.machine.product = False
            self.preventive_op2.create_repair_order()
        repair = self.repair_obj.search(
            [('idmachine', '=', self.machine_1.id),
             ('id', 'in', repair_ids)])[0]
        pre_repair_lines = len(repair.operations)
        self.preventive_op2.machine.product = product2
        self.preventive_op2.create_repair_order()
        final_repairs = len(self.repair_obj.search(
            [('idmachine', '=', self.machine_1.id),
             ('state', 'in', ('draft', 'confirmed', 'ready'))]))
        pos_repair_lines = len(repair.operations)
        self.assertEqual(post_repairs, final_repairs, 'Error in repair_wiz2')
        self.assertNotEqual(pre_repair_lines, pos_repair_lines,
                            'Error in repair_lines_wiz')
        self.preventive_op1.active_repair_order = True
        self.preventive_op1.update_preventive = 'before_repair'
        self.preventive_op1.create_repair_order()
