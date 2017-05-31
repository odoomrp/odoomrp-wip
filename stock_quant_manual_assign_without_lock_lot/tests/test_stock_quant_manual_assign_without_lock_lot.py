# -*- coding: utf-8 -*-
# Copyright © 2017 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.stock_quant_manual_assign.tests\
    .test_stock_quant_manual_assign import TestStockQuantManualAssign
from openerp.tests.common import at_install, post_install


@at_install(False)
@post_install(True)
class TestStockQuantManualAssignWithoutLockLot(TestStockQuantManualAssign):

    def setUp(self):
        super(TestStockQuantManualAssignWithoutLockLot, self).setUp()
