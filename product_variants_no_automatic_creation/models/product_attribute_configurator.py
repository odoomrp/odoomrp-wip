# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductAttributeConfigurator(models.AbstractModel):
    _name = 'product.attribute.configurator'

    @api.one
    @api.depends('attribute')
    def _get_possible_attribute_values(self):
        self.possible_values = self.attribute.value_ids.sorted()

    @api.one
    @api.depends('value')
    def _get_price_extra(self):
        self.price_extra = sum(self.value.mapped('price_ids.price_extra'))

    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            domain="[('attribute_id', '=', attribute),"
                            "('id', 'in', possible_values[0][2])]",
                            string='Value')
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')
    price_extra = fields.Float(
        compute='_get_price_extra', string='Attribute Price Extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with this attribute"
        " value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")


class ProductProductAttribute(models.Model):
    _inherit = 'product.attribute.configurator'
    _name = 'product.product.attribute'

    @api.one
    @api.depends('attribute', 'product.product_tmpl_id',
                 'product.product_tmpl_id.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.product.product_tmpl_id.attribute_line_ids:
            if attr_line.attribute_id.id == self.attribute.id:
                attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()

    @api.one
    @api.depends('value', 'product.product_tmpl_id')
    def _get_price_extra(self):
        price_extra = 0.0
        for price in self.value.price_ids:
            if price.product_tmpl_id.id == self.product.product_tmpl_id.id:
                price_extra = price.price_extra
        self.price_extra = price_extra

    product = fields.Many2one(
        comodel_name='product.product', string='Product')
