# -*- coding: utf-8 -*-
# © 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp.modules.module import get_module_resource
from openerp import exceptions


class TestInventoryLineImport(common.TransactionCase):

    def get_file(self, filename):
        """Retrieve file from test data, encode it as base64 """
        path = get_module_resource('stock_inventory_import',
                                   'tests', 'data', filename)
        test_data = open(path).read()
        return test_data.encode("base64")

    def setUp(self):
        super(TestInventoryLineImport, self).setUp()
        self.inventory = self.env['stock.inventory'].create({
            'name': 'Test Inventory',
            'filter': 'file',
            })
        self.importer = self.env['import.inventory'].create(
            {'data': self.get_file('stock_inventory_line.csv'),
             'delimeter': ',',
             'location': self.ref('stock.stock_location_stock'),
             'name': 'stock_inventory_line',
             }
        )

    def test_import_inventory(self):
        self.importer.with_context({
            'active_id': [self.inventory.id]}).action_import()
        self.assertTrue(len(self.inventory.import_lines), 2)
        self.inventory.process_import_lines()
        self.assertTrue(len(self.inventory.line_ids), 2)

    def test_import_inventory_no_lines_processed(self):
        self.importer.with_context({
            'active_id': [self.inventory.id]}).action_import()
        with self.assertRaises(exceptions.Warning):
            self.inventory.action_done()
