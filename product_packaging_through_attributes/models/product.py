# -*- coding: utf-8 -*-
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import models, fields, api


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_package = fields.Boolean(string='Is a package')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    is_package_attr = fields.Boolean(
        string='Package attribute', related='attribute_id.is_package')
    package_product = fields.Many2one(
        comodel_name='product.product', string='Package Product',
        context="{'default_sale_ok': False, 'default_purchase_ok': False}")


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    product = fields.Many2one(
        comodel_name='product.product', string='Package Product',
        context="{'default_sale_ok': False, 'default_purchase_ok': False}")

    @api.onchange('product')
    def onchange_product(self):
        self.product_tmpl_id = self.product.product_tmpl_id
