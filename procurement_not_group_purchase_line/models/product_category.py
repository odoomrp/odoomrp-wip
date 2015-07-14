# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    group_in_purchase = fields.Boolean(
        string='Group in purchase', default=True,
        help='If the check is marked, running the procurement acts in a'
        ' standard, adding the amount on line purchase order, but if it is not'
        ' checked, a new line will be created in the purchase order.')
