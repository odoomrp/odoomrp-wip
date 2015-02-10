# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_only_allowed = fields.Boolean(
        string="Use in sales only allowed products",
        help="If checked, by default you will only be able to select products "
             "that have this customer added to their customer list when "
             "creating a sale order for it. This value can be changed for "
             "each order.")
