# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    only_products_allowed_in_purchase = fields.Boolean(
        string="Only products allowed in purchase")
