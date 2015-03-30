# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if not res.get('value'):
                res['value'] = {}
            res['value']['product_ul'] = (
                partner.partner_product_ul.id or
                partner.commercial_partner_id.partner_product_ul.id)
        return res

    @api.one
    @api.onchange('product_ul')
    def onchange_product_ul(self):
        for line in self.order_line:
            line.sec_pack = line.sec_pack or self.product_ul


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.one
    @api.depends('order_id.product_ul', 'product_id', 'product_qty',
                 'pri_pack', 'sec_pack')
    def _calculate_packages(self):
        package_attr = self.product_id.attribute_value_ids.filtered(
            lambda x: x.attribute_id.is_package)
        if package_attr:
            self.pri_pack_qty = (
                self.product_qty / (package_attr.numeric_value or 1.0))
            if package_attr.package_product:
                self.pri_pack = package_attr.package_product
                for packaging in self.sec_pack.packagings:
                    if packaging.product == package_attr.package_product:
                        self.sec_pack_qty = (
                            self.pri_pack_qty / (
                                (packaging.ul_qty * packaging.rows) or 1.0))

    pri_pack_qty = fields.Float(
        string='# Pkg 1', compute='_calculate_packages', digits=(12, 2),
        store=True)
    pri_pack = fields.Many2one(
        comodel_name='product.product', string='Pkg 1',
        compute='_calculate_packages', readonly=True)
    sec_pack_qty = fields.Float(
        string='# Pkg 2', compute='_calculate_packages', digits=(12, 2),
        store=True)
    sec_pack = fields.Many2one(
        comodel_name='product.ul', string='Pkg 2')
