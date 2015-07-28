# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class WizProductionProductLine(models.TransientModel):
    _inherit = 'wiz.production.product.line'

    @api.multi
    def add_product(self):
        return super(
            WizProductionProductLine,
            self.with_context(work_order=self.work_order)).add_product()
