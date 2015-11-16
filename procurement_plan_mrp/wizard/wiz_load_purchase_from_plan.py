# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class WizLoadPurchaseFromPlan(models.TransientModel):

    _inherit = 'wiz.load.purchase.from.plan'

    @api.multi
    def _prepare_vals_for_procurement(self, prod_vals, plan, product, date):
        vals = super(
            WizLoadPurchaseFromPlan, self)._prepare_vals_for_procurement(
            prod_vals, plan, product, date)
        vals['level'] = 1000
        return vals
