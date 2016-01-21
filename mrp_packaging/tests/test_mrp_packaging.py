# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpPackaging(common.TransactionCase):

    def setUp(self):
        super(TestMrpPackaging, self).setUp()
        self.attr_value_model = self.env['product.attribute.value']
        self.product_model = self.env['product.product']
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.unit_uom = self.env.ref('product.product_uom_unit')
        self.kg_uom = self.env.ref('product.product_uom_kgm')
        self.box_product = self.product_model.create({
            'name': 'Box',
            'type': 'product',
            'uom_id': self.unit_uom.id,
            'uom_po_id': self.unit_uom.id,
        })
        self.package_attribute = self.env['product.attribute'].create({
            'name': 'Package',
            'attr_type': 'numeric',
        })
        self.package_value = self.attr_value_model.create({
            'name': '25 per box',
            'attribute_id': self.package_attribute.id,
            'numeric_value': 25.0,
            'raw_product': self.box_product.id,
        })
        self.bulk_product = self.product_model.create({
            'name': 'Bulk Product',
            'type': 'product',
            'uom_id': self.kg_uom.id,
            'uom_po_id': self.kg_uom.id,
        })
        self.bulk_component = self.product_model.create({
            'name': 'Bulk Component',
            'type': 'product',
            'uom_id': self.kg_uom.id,
            'uom_po_id': self.kg_uom.id,
        })
        self.packaged_product1 = self.product_model.create({
            'name': 'Packaged Product (1)',
            'type': 'product',
            'uom_id': self.kg_uom.id,
            'uom_po_id': self.kg_uom.id,
            'attribute_value_ids': [(4, self.package_value.id)],
        })
        self.packaged_product2 = self.product_model.create({
            'name': 'Packaged Product (2)',
            'type': 'product',
            'uom_id': self.unit_uom.id,
            'uom_po_id': self.unit_uom.id,
            'attribute_value_ids': [(4, self.package_value.id)],
        })
        self.bulk_bom = self.bom_model.create({
            'name': 'Bulk Product BoM',
            'product_tmpl_id': self.bulk_product.product_tmpl_id.id,
            'product_id': self.bulk_product.id,
            'product_qty': 1.0,
            'product_uom': self.bulk_product.uom_id.id,
            'type': 'normal',
            'active': 'True',
            'state': 'active',
            'bom_line_ids': [(0, 0, {
                'product_id': self.bulk_component.id,
                'product_qty': 1.0,
                'product_uom': self.kg_uom.id,
                'type': 'normal',
            })],
        })
        self.packaged_bom1 = self.bom_model.create({
            'name': 'Packaged Product BoM (1)',
            'product_tmpl_id': self.packaged_product1.product_tmpl_id.id,
            'product_id': self.packaged_product1.id,
            'product_qty': 1.0,
            'product_uom': self.packaged_product1.uom_id.id,
            'type': 'normal',
            'active': 'True',
            'state': 'active',
            'bom_line_ids': [(0, 0, {
                'product_id': self.bulk_product.id,
                'product_qty': 1.0,
                'product_uom': self.kg_uom.id,
                'type': 'normal',
            })],
        })
        self.packaged_bom2 = self.bom_model.create({
            'name': 'Packaged Product BoM (2)',
            'product_tmpl_id': self.packaged_product2.product_tmpl_id.id,
            'product_id': self.packaged_product2.id,
            'product_qty': 1.0,
            'product_uom': self.packaged_product2.uom_id.id,
            'type': 'normal',
            'active': 'True',
            'state': 'active',
            'bom_line_ids': [(0, 0, {
                'product_id': self.bulk_product.id,
                'product_qty': 1.0,
                'product_uom': self.kg_uom.id,
                'type': 'normal',
            })],
        })
        self.bulk_production = self.production_model.create({
            'product_id': self.bulk_product.id,
            'product_qty': 50.0,
            'product_uom': self.bulk_product.uom_id.id,
            'bom_id': self.bulk_bom.id,
        })
        self.bulk_production.signal_workflow('button_confirm')
        self.bulk_production.force_production()
        self.bulk_production.action_produce(
            self.bulk_production.id, self.bulk_production.product_qty,
            'consume_produce')
        self.bulk_production.get_dump_packages()
        self.pack_qty = 1.0
        self.fill = 26.0

    def test_bulk_production_done(self):
        self.assertIn(
            self.bulk_production.state, ['in_production', 'done'])
        self.assertNotEquals(self.bulk_production.pack, False)
        self.assertEqual(self.bulk_production.product_qty,
                         self.bulk_production.final_product_qty)
        self.assertEqual(self.bulk_production.product_qty,
                         self.bulk_production.left_product_qty)

    def test_packaging_same_uom(self):
        pack = self.bulk_production.pack.filtered(
            lambda x: x.product == self.packaged_product1)
        pack.write({
            'qty': self.pack_qty,
            'fill': self.fill,
        })
        self.bulk_production.create_mo_from_packaging_operation()
        self.assertNotEquals(self.bulk_production.expected_production, False)
        production = self.bulk_production.expected_production.filtered(
            lambda x: x.product_id == self.packaged_product1)
        self.assertEquals(production.product_qty, self.fill)
        for line in production.product_lines:
            if line.product_id == self.bulk_product:
                self.assertEquals(line.product_qty, self.fill)
            elif line.product_id == self.box_product:
                self.assertEquals(line.product_qty, self.pack_qty)
        production.signal_workflow('button_confirm')
        self.assertEqual(self.bulk_production.product_qty - self.fill,
                         self.bulk_production.left_product_qty)

    def test_packaging_different_uom(self):
        pack = self.bulk_production.pack.filtered(
            lambda x: x.product == self.packaged_product2)
        pack.write({
            'qty': self.pack_qty,
            'fill': self.fill,
        })
        self.bulk_production.create_mo_from_packaging_operation()
        self.assertNotEquals(self.bulk_production.expected_production, False)
        production = self.bulk_production.expected_production.filtered(
            lambda x: x.product_id == self.packaged_product2)
        self.assertEquals(production.product_qty, self.pack_qty)
        for line in production.product_lines:
            if line.product_id == self.bulk_product:
                self.assertEquals(line.product_qty, self.fill)
            elif line.product_id == self.box_product:
                self.assertEquals(line.product_qty, self.pack_qty)
