# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    raw_product = fields.Many2one('product.product',
                                  string='Raw Product')
    raw_qty = fields.Float(string='Raw Product QTY', default=1.)
