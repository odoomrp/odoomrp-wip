# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestStockInvoicingType(common.TransactionCase):

    def setUp(self):
        super(TestStockInvoicingType, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.procurement_model = self.env['procurement.order']
        self.picking_model = self.env['stock.picking']
        self.picking_type_model = self.env['stock.picking.type']
        self.invoice_wizard_model = self.env['stock.invoice.onshipping']
        self.partner = self.browse_ref('base.res_partner_2')
        self.product = self.browse_ref('product.product_product_3')
        self.grouped_type_id = self.ref('sale_journal.monthly')
        self.nogrouped_type_id = self.ref('sale_journal.daily')
        self.sale_order = self.sale_order_model.create({
            'partner_id': self.ref('base.res_partner_2'),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
            })],
        })
        self.sale_order.action_button_confirm()

    def test_procurement_run(self):
        procurement = self.procurement_model.search(
            [('origin', '=', self.sale_order.name),
             ('product_id', '=', self.product.id)])
        self.assertEqual(
            len(procurement), 1, "Procurement not generated for product.")
        procurement.run()
        for picking in procurement.mapped('move_ids.picking_id'):
            self.assertEqual(
                picking.invoice_type_id, self.sale_order.invoice_type_id,
                "Sale order and Picking must have the same invoice type.")

    def test_onchange_partner_id(self):
        picking_type = self.picking_type_model.search(
            [('code', '=', 'outgoing')], limit=1)
        onchange = self.picking_model.onchange_partner_id(self.partner.id)
        picking = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type[:1].id,
            'invoice_type_id': onchange['value']['invoice_type_id'],
        })
        self.assertEqual(
            picking.invoice_type_id, self.partner.property_invoice_type,
            "Invoice type must have been taken from partner.")

    def test_create_invoices(self):
        picking_type = self.picking_type_model.search(
            [('code', '=', 'outgoing')], limit=1)
        picking1 = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type[:1].id,
            'invoice_type_id': self.grouped_type_id,
            'invoice_state': '2binvoiced',
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'location_id': picking_type[:1].default_location_src_id.id,
                'location_dest_id': (
                    picking_type[:1].default_location_dest_id.id)})],
        })
        picking2 = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type[:1].id,
            'invoice_type_id': self.grouped_type_id,
            'invoice_state': '2binvoiced',
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'location_id': picking_type[:1].default_location_src_id.id,
                'location_dest_id': (
                    picking_type[:1].default_location_dest_id.id)})]
        })
        picking3 = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type[:1].id,
            'invoice_type_id': self.nogrouped_type_id,
            'invoice_state': '2binvoiced',
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'location_id': picking_type[:1].default_location_src_id.id,
                'location_dest_id': (
                    picking_type[:1].default_location_dest_id.id)})]
        })
        active_ids = (picking1 + picking2 + picking3)
        journal2type = {
            'sale': 'out_invoice', 'purchase': 'in_invoice',
            'sale_refund': 'out_refund', 'purchase_refund': 'in_refund'}
        journal_id = self.invoice_wizard_model._get_journal()
        journal_type = self.invoice_wizard_model._get_journal_type()
        inv_type = journal2type.get(journal_type) or 'out_invoice'
        invoices = active_ids.action_invoice_create(
            journal_id=journal_id, type=inv_type)
        self.assertEqual(
            len(invoices), 2, 'There must have been created 2 invoices.')
