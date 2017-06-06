# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos - AvanzOSC
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
import base64
import os


class TestProductPricelistImport(common.TransactionCase):

    def setUp(self):
        super(TestProductPricelistImport, self).setUp()
        self.load_obj = self.env['product.pricelist.load']
        self.wiz_obj = self.env['import.price.file']

    def test_product_pricelist_import_csv(self):
        path = os.path.abspath(os.path.dirname(__file__))
        path += '/product_load.csv'
        file = open(path, 'r')
        datas = base64.encodestring(file.read())
        file.close()
        load_vals = {'name': 'load - 1',
                     'supplier': self.ref('base.res_partner_16')}
        load = self.load_obj.create(load_vals)
        wiz_vals = {'data': datas,
                    'file_type': 'csv',
                    'delimeter': ';'}
        wiz = self.wiz_obj.create(wiz_vals)
        wiz.with_context(
            active_id=load.id).action_import()
        load.process_lines()
        self.assertEquals(
            len(load.mapped('file_lines').filtered(lambda x: x.fail)), 1,
            'It was not found row without processing')
        supplier = self.browse_ref('product.product_product_8').mapped(
            'supplier_ids').filtered(lambda x: x.name.id ==
                                     self.ref('base.res_partner_16'))
        self.assertEquals(
            supplier.pricelist_ids[0].price, 88.99, 'Price must be 88.99')
        supplier = self.browse_ref('product.product_product_6').mapped(
            'supplier_ids').filtered(lambda x: x.name.id ==
                                     self.ref('base.res_partner_16'))
        self.assertEquals(
            supplier.pricelist_ids[0].price, 33.22, 'Price must be 33.22')
        supplier = self.browse_ref('stock.product_icecream').mapped(
            'supplier_ids').filtered(lambda x: x.name.id ==
                                     self.ref('base.res_partner_16'))
        self.assertEquals(
            supplier.pricelist_ids[0].price, 7.28, 'Price must be 7.28')
