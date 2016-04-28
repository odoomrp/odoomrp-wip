# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_only_allowed = fields.Boolean(
        string="Use in sales only allowed products",
        help="If checked, by default you will only be able to select products "
             "that have this customer added to their customer list when "
             "creating a sale order for it. This value can be changed for "
             "each order.")
