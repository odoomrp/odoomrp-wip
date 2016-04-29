# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models
from openerp.osv import fields as old_fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Redefine the column in old API to overwrite the related non stored field
    _columns = {
        'product_tmpl_id': old_fields.many2one(
            'product.template', string='Product Template', readonly=False),
    }
