# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestStockQuantPackagesMovingWizard(common.TransactionCase):

    def setUp(self):
        super(TestStockQuantPackagesMovingWizard, self).setUp()
        quant_model = self.env['stock.quant']
        package_model = self.env['stock.quant.package']
        self.quant_move_model = self.env['stock.quant.move']
        self.quant_move_item_model = self.env['stock.quant.move_items']
        self.quants_move_model = self.env['stock.quants.move']
        self.quants_move_item_model = self.env['stock.quants.move_items']
        self.package_move_model = self.env['stock.quant.package.move']
        self.package_move_item_model =\
            self.env['stock.quant.package.move_items']
        self.location_from_id = self.ref('stock.location_production')
        self.location_to_id = self.ref('stock.stock_location_stock')
        product = self.env['product.product'].create({
            'name': 'Stockable Product for Test',
            'type': 'product',
        })
        self.quant1 = quant_model.create({
            'product_id': product.id,
            'qty': 150.0,
            'location_id': self.location_from_id,
        })
        self.quant2 = quant_model.create({
            'product_id': product.id,
            'qty': 150.0,
            'location_id': self.location_from_id,
        })
        self.package1 = package_model.create({
            'name': 'Package for Test',
        })
        self.package2 = package_model.create({
            'name': 'Package for Test (children)',
            'parent_id': self.package1.id,
            'quant_ids': [(6, 0, self.quant2.ids)],
        })
        self.assertEquals(self.quant2.package_id, self.package2)
        self.assertEquals(self.quant1.location_id.id, self.location_from_id)
        self.assertEquals(self.quant2.location_id.id, self.location_from_id)
        self.assertEquals(self.package1.location_id.id, self.location_from_id)
        self.assertEquals(self.package2.location_id.id, self.location_from_id)

    def test_move_quant(self):
        move_wiz = self.quant_move_model.create({
            'pack_move_items': [(0, 0,
                                 {'quant': self.quant1.id,
                                  'dest_loc': self.location_to_id})],
        })
        move_wiz.do_transfer()
        self.assertEquals(self.quant1.location_id.id, self.location_to_id)

    def test_move_quant_default(self):
        move_wiz_vals = self.quant_move_model.with_context(
            active_ids=self.quant1.ids).default_get([])
        self.assertEquals(
            move_wiz_vals['pack_move_items'][0]['quant'], self.quant1.id)

    def test_move_package_default(self):
        move_wiz_vals = self.package_move_model.with_context(
            active_ids=self.package1.ids).default_get([])
        self.assertEquals(
            move_wiz_vals['pack_move_items'][0]['package'], self.package1.id)

    def test_move_quant_package(self):
        move_wiz = self.package_move_model.create({
            'pack_move_items': [(0, 0,
                                 {'package': self.package1.id,
                                  'dest_loc': self.location_to_id})],
        })
        move_wiz.do_detailed_transfer()
        self.assertEquals(self.quant2.location_id.id, self.location_to_id)
        # It fails here because of a bug in the module
        # quant2 is not inside the package2
        self.assertEquals(self.quant2.package_id, self.package2)
        self.assertEquals(self.package1.location_id.id, self.location_to_id)
        self.assertEquals(self.package2.location_id.id, self.location_to_id)
