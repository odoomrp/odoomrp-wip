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
    def calculate_packaging_qty(self):
        for attr_value in self.product_id.attribute_value_ids:
            if attr_value.attribute_id.is_packaging:
                self.packaging_qty = (
                    self.product_uom_qty / (attr_value.numeric_value or 1.0))

    @api.one
    @api.depends('order_id.product_ul', 'packaging_qty')
    def calculate_pallet_qty(self):
        for attr_value in self.product_id.attribute_value_ids:
            if attr_value.attribute_id.is_packaging:
                product = attr_value.packaging_product
        for packaging in self.order_id.product_ul.packagings:
            if (product and
                    packaging.product_tmpl_id == product.product_tmpl_id):
                self.pallet_qty = (
                    self.packaging_qty / (
                        (packaging.ul_qty * packaging.rows) or 1.0))

    packaging_qty = fields.Float(
        string='# Packaging', compute='calculate_packaging_qty',
        store=True)
    pallet_qty = fields.Float(
        string='# Pallet',
        compute='calculate_pallet_qty', store=True)
