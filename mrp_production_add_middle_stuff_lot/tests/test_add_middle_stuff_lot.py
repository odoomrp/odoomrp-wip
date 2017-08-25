# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.mrp_production_add_middle_stuff.tests\
    .test_mrp_production_add_middle_stuff import\
    TestMrpProductionAddMiddleStuff
from openerp import exceptions


class TestMrpProductionAddMiddleStuffLot(TestMrpProductionAddMiddleStuff):

    def setUp(self):
        super(TestMrpProductionAddMiddleStuffLot, self).setUp()
        self.lot = self.env['stock.production.lot'].create({
            'name': 'Lot',
            'product_id': self.product1.id,
        })

    def test_add_middle_stuff_lot(self):
        self.production.action_confirm()
        self.assertTrue(self.production.product_lines)
        self.assertEquals(len(self.production.move_lines), 1)
        self.assertFalse(self.production.product_lines.filtered('addition'))
        wiz_values = {
            'product_id': self.product1.id,
            'product_qty': 1.0,
            'product_uom_id': self.product1.uom_id.id,
            'lot': self.lot.id,
        }
        add_stuff = self.middle_model.with_context(
            active_id=self.production.id,
            active_model=self.production._model._name).create(wiz_values)
        with self.assertRaises(exceptions.Warning):
            add_stuff.add_product()
        self.env['stock.quant'].sudo().create({
            'product_id': self.product1.id,
            'qty': 10.0,
            'lot_id': self.lot.id,
            'location_id': self.production.location_src_id.id,
        })
        add_stuff.add_product()
        self.assertTrue(self.production.product_lines.filtered('addition'))
        self.assertEquals(len(self.production.move_lines), 2)

    def test_add_middle_stuff(self):
        """ pass """

    def test_add_middle_stuff_onchange(self):
        """ pass """
