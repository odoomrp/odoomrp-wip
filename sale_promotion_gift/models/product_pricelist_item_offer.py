# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductPricelistItemOffer(models.Model):
    _inherit = 'product.pricelist.item.offer'

    gift_products = fields.One2many(
        'gift.product', 'product_pricelist_item_offer',
        string='Gift products', copy=False)
