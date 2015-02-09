# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_packaging = fields.Boolean(string='Is packaging')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    is_packaging_attr = fields.Boolean(
        string='Packaging attribute', related='attribute_id.is_packaging')
    packaging_product = fields.Many2one(
        comodel_name='product.product', string='Packaging Product')


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    product = fields.Many2one(
        comodel_name='product.product', string='Packging Product')

    @api.one
    @api.onchange('product')
    def onchange_product(self):
        self.product_tmpl_id = self.product.product_tmpl_id
