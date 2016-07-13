# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta


class TestMrpPackagingExpiry(common.TransactionCase):

    def setUp(self):
        super(TestMrpPackagingExpiry, self).setUp()
        self.attr_value_model = self.env['product.attribute.value']
        self.lot_model = self.env['stock.production.lot']
        self.product_model = self.env['product.product']
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.move_model = self.env['stock.move']
        self.unit_uom = self.ref('product.product_uom_unit')
        self.kg_uom = self.ref('product.product_uom_kgm')
        self.box_product = self.product_model.create({
            'name': 'Box',
            'type': 'product',
            'uom_id': self.unit_uom,
            'uom_po_id': self.unit_uom,
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
            'uom_id': self.kg_uom,
            'uom_po_id': self.kg_uom,
        })
        self.bulk_component = self.product_model.create({
            'name': 'Bulk Component',
            'type': 'product',
            'uom_id': self.kg_uom,
            'uom_po_id': self.kg_uom,
        })
        self.packaged_product1 = self.product_model.create({
            'name': 'Packaged Product (1)',
            'type': 'product',
            'uom_id': self.kg_uom,
            'uom_po_id': self.kg_uom,
            'attribute_value_ids': [(4, self.package_value.id)],
        })
        self.packaged_product2 = self.product_model.create({
            'name': 'Packaged Product (2)',
            'type': 'product',
            'uom_id': self.unit_uom,
            'uom_po_id': self.unit_uom,
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
                'product_uom': self.kg_uom,
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
                'product_uom': self.kg_uom,
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
                'product_uom': self.kg_uom,
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
        self.bulk_lot = self.lot_model.create(
            {'name': 'bulk_manual_lot', 'product_id': self.bulk_product.id})
        wiz = self.create_production_wiz(self.bulk_production, self.bulk_lot)
        self.bulk_production.action_produce(
            self.bulk_production.id, self.bulk_production.product_qty,
            'consume_produce', wiz=wiz)
        self.bulk_production.get_dump_packages()
        self.pack_qty = 1.0
        self.fill = 26.0

    def create_production_wiz(self, production, lot):
        wiz_model = self.env['mrp.product.produce']
        consume_lines = []
        for line in self.production_model._calculate_qty(
                production, production.product_qty):
            consume_lines.append(tuple([0, 0, line]))
        vals = {
            'product_id': production.product_id.id,
            'product_qty': production.product_qty,
            'mode': 'consume_produce',
            'lot_id': lot.id,
            'consume_lines': consume_lines}
        return wiz_model.create(vals)

    def test_bulk_production_lot_dates(self):
        moves = self.move_model.search([('production_id', '=',
                                         self.bulk_production.id),
                                        ('state', '!=', 'cancel')])
        lots = moves.mapped('lot_ids') | moves.mapped('restrict_lot_id')
        removal_date = (fields.Date.from_string(fields.Date.today()) +
                        relativedelta(months=1))
        life_date = removal_date + relativedelta(days=3)
        alert_date = removal_date - relativedelta(weeks=1)
        use_date = removal_date + relativedelta(days=2)
        lots.write({'removal_date': removal_date,
                    'life_date': life_date,
                    'alert_date': alert_date,
                    'use_date': use_date})
        pack = self.bulk_production.pack.filtered(
            lambda x: x.product == self.packaged_product2)
        pack.write({
            'qty': self.pack_qty,
            'fill': self.fill,
        })
        self.bulk_production.create_mo_from_packaging_operation()
        production = self.bulk_production.expected_production[:1]
        production.signal_workflow('button_confirm')
        production.force_production()
        lot = self.lot_model.create(
            {'name': 'production_manual_lot',
             'product_id': production.product_id.id})
        wiz = self.create_production_wiz(production, lot)
        production.action_produce(
            production.id, production.product_qty, 'consume_produce', wiz=wiz)
        production_moves = production.move_created_ids2.filtered(
            lambda x: x.state != 'cancel')
        lot = (production_moves.mapped('lot_ids') |
               production_moves.mapped('restrict_lot_id'))[:1]
        self.assertEqual(lot.removal_date,
                         fields.Datetime.to_string(removal_date),
                         'Removal Date Incorrect')
        self.assertEqual(lot.life_date, fields.Datetime.to_string(life_date),
                         'Life Date Incorrect')
        self.assertEqual(lot.alert_date, fields.Datetime.to_string(alert_date),
                         'Alert Date Incorrect')
        self.assertEqual(lot.use_date, fields.Datetime.to_string(use_date),
                         'Use Date Incorrect')
