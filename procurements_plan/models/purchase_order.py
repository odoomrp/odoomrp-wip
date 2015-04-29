# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    plan = fields.Many2one('procurement.plan', string='Plan')
