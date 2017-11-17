# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_ok = fields.Boolean(select=True)


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    name = fields.Many2one(select=True)
