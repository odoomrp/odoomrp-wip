# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.one
    @api.onchange('product_ul')
    def onchange_product_ul(self):
        for line in self.order_line:
            line.sec_pack = line.sec_pack or self.product_ul


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('order_id.product_ul', 'product_id', 'product_uom_qty')
    def _calculate_packages(self):
        package_attr = False
        for attr_value in self.product_id.attribute_value_ids:
            if attr_value.attribute_id.is_package:
                package_attr = attr_value
                break
        if package_attr:
            self.pri_pack_qty = (
                self.product_uom_qty / (package_attr.numeric_value or 1.0))
            if package_attr.package_product:
                self.pri_pack = package_attr.package_product
                for packaging in self.sec_pack.packagings:
                    if packaging.product == package_attr.package_product:
                        self.sec_pack_qty = (
                            self.pri_pack_qty / (
                                (packaging.ul_qty * packaging.rows) or 1.0))

    pri_pack_qty = fields.Float(
        string='# Pkg 1', compute='_calculate_packages', store=True)
    pri_pack = fields.Many2one(
        comodel_name='product.product', string='Pkg 1',
        compute='_calculate_packages', readonly=True)
    sec_pack_qty = fields.Float(
        string='# Pkg 2', compute='_calculate_packages', store=True)
    sec_pack = fields.Many2one(
        comodel_name='product.ul', string='Pkg 2')
