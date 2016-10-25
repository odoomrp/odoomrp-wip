# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestMrpRepairFullEditable(common.TransactionCase):

    def setUp(self):
        super(TestMrpRepairFullEditable, self).setUp()
        self.mrp_repair = self.env.ref('mrp_repair.mrp_repair_rmrp1')
        self.product = self.ref('product.product_product_2')
        self.pricelist = self.env.ref('product.list0')

    def test_onchange_product_id(self):
        self.mrp_repair.partner_id = ''
        self.mrp_repair.product_id = self.product
        res = self.mrp_repair.onchange_product_id()
        self.assertEqual(res['value']['pricelist_id'], self.pricelist)
