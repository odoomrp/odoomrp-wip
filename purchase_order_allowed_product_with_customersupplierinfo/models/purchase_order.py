# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_allowed_product_domain(self):
        result = super(PurchaseOrder, self)._prepare_allowed_product_domain()
        result.extend([('type', '=', 'supplier')])
        return result
