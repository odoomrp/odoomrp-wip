# -*- coding: utf-8 -*-

from openerp import models, fields


class ProductPricelistItemOffer(models.Model):
    _inherit = 'product.pricelist.item.offer'

    sale_promotion_gifts = fields.One2many(
        comodel_name='sale.promotion.gift',
        inverse_name='product_pricelist_item_offer',
        string='Sale promotion gifts', copy=False)
    not_combinable = fields.Boolean(string='Offer not combinable')
