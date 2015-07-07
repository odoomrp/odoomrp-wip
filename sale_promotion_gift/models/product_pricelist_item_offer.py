# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductPricelistItemOffer(models.Model):
    _inherit = 'product.pricelist.item.offer'

    sale_promotion_gifts = fields.One2many(
        'sale.promotion.gift', 'product_pricelist_item_offer',
        string='Sale promotion gifts', copy=False)
    not_combinable = fields.Boolean('Offer not combinable')
