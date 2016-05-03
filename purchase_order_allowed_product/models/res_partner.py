# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_only_allowed = fields.Boolean(
        string="Use in purchases only allowed products",
        help="If checked, by default you will only be able to select products"
             " that can be supplied by this supplier when creating a purchase"
             " order for it. This value can be changed for each order.")
