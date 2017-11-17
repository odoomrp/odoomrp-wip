# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions


class TestMrpProductionAddMiddleStuff(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionAddMiddleStuff, self).setUp()
        production_model = self.env['mrp.production']
        product_model = self.env['product.product']
        unit_uom = self.browse_ref('product.product_uom_unit')
        self.unit_kg = self.browse_ref('product.product_uom_kgm')
        product = product_model.create({
            'name': 'Production Product',
            'uom_id': unit_uom.id,
        })
        self.product1 = product_model.create({
            'name': 'Consume Product',
            'uom_id': unit_uom.id,
        })
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_id': product.id,
            'bom_line_ids': [(0, 0, {
                'product_id': self.product1.id,
                'product_qty': 1.0,
                'product_uom': self.product1.uom_id.id,
            })]
        })
        self.production = production_model.create({
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'bom_id': bom.id,
        })
        self.middle_model = self.env['wiz.production.product.line']
        self.production.action_compute()

    def test_add_middle_stuff(self):
        self.production.action_confirm()
        self.assertTrue(self.production.product_lines)
        self.assertEquals(len(self.production.move_lines), 1)
        self.assertFalse(self.production.product_lines.filtered('addition'))
        wiz_values = {
            'product_id': self.product1.id,
            'product_qty': 0.0,
            'product_uom_id': self.unit_kg.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            self.middle_model.with_context(
                active_id=self.production.id,
                active_model=self.production._model._name).create(wiz_values)
        wiz_values.update({'product_uom_id': self.product1.uom_id.id})
        add_stuff = self.middle_model.with_context(
            active_id=self.production.id,
            active_model=self.production._model._name).create(wiz_values)
        with self.assertRaises(exceptions.Warning):
            add_stuff.add_product()
        add_stuff.write({
            'product_qty': 1.0,
        })
        add_stuff.add_product()
        self.assertTrue(self.production.product_lines.filtered('addition'))
        self.assertEquals(len(self.production.move_lines), 2)

    def test_add_middle_stuff_onchange(self):
        wiz_values = {
            'product_id': self.product1.id,
        }
        add_stuff = self.middle_model.with_context(
            active_id=self.production.id).new(wiz_values)
        self.assertFalse(add_stuff.product_qty)
        self.assertFalse(add_stuff.product_uom_id)
        add_stuff.onchange_product_id()
        self.assertEquals(add_stuff.product_qty, 1.0)
        self.assertEquals(add_stuff.product_uom_id, self.product1.uom_id)
