# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class PromotionGiftProduct(models.Model):
    _name = 'promotion.gift.product'
    _description = 'Promotion gift product'

    product_pricelist_item_offer = fields.Many2one(
        'product.pricelist.item.offer', string='Pricelist item offer',
        copy=False, ondelete='cascade')
    product = fields.Many2one(
        'product.product', string='Product', required=True)
    category = fields.Many2one(
        'product.category', 'Category', related="product.categ_id",
        store=True, readonly=True)
    quantity = fields.Integer(string='Quantity', required=True)
