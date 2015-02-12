# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_only_allowed = fields.Boolean(
        string="Use in purchases only allowed products",
        help="If checked, by default you will only be able to select products"
             " that can be supplied by this supplier when creating a purchase"
             " order for it. This value can be changed for each order.")
