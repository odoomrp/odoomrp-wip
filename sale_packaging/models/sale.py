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

    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')

    @api.one
    @api.depends('product_ul', 'product_uom_qty')
    def calculate_product_ul_qty(self):
        self.product_ul_qty = self.product_uom_qty

    @api.one
    @api.depends('order_id.product_ul', 'product_ul_qty')
    def calculate_order_product_ul_qty(self):
        self.order_product_ul_qty = self.product_ul_qty

    product_ul_qty = fields.Float(
        string='Logistic Unit Quantity', compute='calculate_product_ul_qty',
        store=True)
    order_product_ul_qty = fields.Float(
        string='Order Logistic Unit Quantity',
        compute='calculate_order_product_ul_qty', store=True)
