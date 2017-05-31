# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.mrp_production_add_middle_stuff.tests\
    .test_mrp_production_add_middle_stuff import\
    TestMrpProductionAddMiddleStuff


class TestAddMiddleStuffOperations(TestMrpProductionAddMiddleStuff):

    def setUp(self):
        super(TestAddMiddleStuffOperations, self).setUp()
        workcenter = self.env['mrp.workcenter'].create({
            'name': 'Workcenter',
        })
        routing = self.env['mrp.routing'].create({
            'name': 'Routing',
            'workcenter_lines': [(0, 0, {'name': 'Operation',
                                         'do_production': True,
                                         'workcenter_id': workcenter.id})]
        })
        self.production.bom_id.write({
            'routing_id': routing.id,
        })
        self.production.bom_id.bom_line_ids.write({
            'operation': routing.workcenter_lines[:0].id,
        })
        self.production.action_compute()

    def test_add_middle_stuff_mo_operations(self):
        self.production.action_confirm()
        self.assertTrue(self.production.product_lines)
        self.assertTrue(self.production.workcenter_lines)
        self.assertEquals(len(self.production.move_lines), 1)
        self.assertFalse(self.production.product_lines.filtered('addition'))
        wiz_values = {
            'product_id': self.product1.id,
            'product_qty': 1.0,
            'product_uom_id': self.product1.uom_id.id,
            'work_order': self.production.workcenter_lines[:1].id,
        }
        add_stuff = self.middle_model.with_context(
            active_id=self.production.id,
            active_model=self.production._model._name).create(wiz_values)
        add_stuff.add_product()
        self.assertTrue(self.production.product_lines.filtered('addition'))
        self.assertEquals(len(self.production.move_lines), 2)

    def test_add_middle_stuff_wo_operations(self):
        self.production.action_confirm()
        self.assertTrue(self.production.product_lines)
        self.assertTrue(self.production.workcenter_lines)
        self.assertEquals(len(self.production.move_lines), 1)
        self.assertFalse(self.production.product_lines.filtered('addition'))
        workorder = self.production.workcenter_lines[:1]
        wiz_values = {
            'product_id': self.product1.id,
            'product_qty': 1.0,
            'product_uom_id': self.product1.uom_id.id,
        }
        add_stuff = self.middle_model.with_context(
            active_id=workorder.id,
            active_model=workorder._model._name).create(wiz_values)
        add_stuff.add_product()
        self.assertTrue(self.production.product_lines.filtered('addition'))
        self.assertEquals(len(self.production.move_lines), 2)

    def test_add_middle_stuff(self):
        """ pass """

    def test_add_middle_stuff_onchange(self):
        """ pass """
