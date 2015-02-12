# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit', readonly=True,
        states={'draft': [('readonly', False)]})


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
                self.pri_pack = _('%.2f %s' %
                                  (self.pri_pack_qty,
                                   package_attr.package_product.name))
                for packaging in self.order_id.product_ul.packagings:
                    if packaging.product == package_attr.package_product:
                        self.sec_pack_qty = (
                            self.pri_pack_qty / (
                                (packaging.ul_qty * packaging.rows) or 1.0))

    pri_pack_qty = fields.Float(
        string='# Primary Packages', compute='_calculate_packages',
        store=True)
    pri_pack = fields.Char(
        string='# Primary Packages', compute='_calculate_packages')
    sec_pack_qty = fields.Float(
        string='# Secondary Packages', compute='_calculate_packages',
        store=True)
