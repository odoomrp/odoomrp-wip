# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('order_id.product_ul', 'product_id', 'product_uom_qty')
    def calculate_product_ul_qty(self):
        for attr_value in self.product_id.attribute_value_ids:
            if attr_value.attribute_id.is_package:
                self.product_ul_qty = (
                    self.product_uom_qty / (attr_value.numeric_value or 1.0))

    @api.one
    @api.depends('order_id.product_ul', 'product_ul_qty')
    def calculate_order_product_ul_qty(self):
        for attr_value in self.product_id.attribute_value_ids:
            if attr_value.attribute_id.is_package:
                product = attr_value.product
        for packaging in self.order_id.product_ul.packagings:
            if (product and
                    packaging.product_tmpl_id == product.product_tmpl_id):
                self.order_product_ul_qty = (
                    self.product_ul_qty / (
                        (packaging.ul_qty * packaging.rows) or 1.0))

    product_ul_qty = fields.Float(
        string='# Packaging', compute='calculate_product_ul_qty',
        store=True)
    order_product_ul_qty = fields.Float(
        string='# Pallet',
        compute='calculate_order_product_ul_qty', store=True)
