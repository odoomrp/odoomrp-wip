# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if not res.get('value'):
                res['value'] = {}
            res['value']['product_ul_id'] = (
                partner.partner_product_ul_id.id or
                partner.commercial_partner_id.partner_product_ul_id.id)
        return res

    @api.onchange('product_ul_id')
    def onchange_product_ul_id(self):
        for record in self:
            for line in record.order_line:
                line.sec_pack_id = line.sec_pack_id or record.product_ul_id


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.one
    @api.depends('order_id.product_ul_id', 'product_id', 'product_qty',
                 'pri_pack_id', 'sec_pack_id')
    def _calculate_packages(self):
        package_attr = self.product_id.attribute_value_ids.filtered(
            lambda x: x.attribute_id.is_package)
        if package_attr:
            self.pri_pack_qty = (
                self.product_qty / (package_attr.numeric_value or 1.0))
            if package_attr.package_product_id:
                self.pri_pack_id = package_attr.package_product_id
                for packaging in self.sec_pack_id.packagings:
                    if packaging.product == package_attr.package_product:
                        self.sec_pack_qty = (
                            self.pri_pack_qty / (
                                (packaging.ul_qty * packaging.rows) or 1.0))

    pri_pack_qty = fields.Float(
        string='# Pkg 1', compute='_calculate_packages',
        digits=dp.get_precision('Product Unit of Measure'), store=True)
    pri_pack_id = fields.Many2one(
        comodel_name='product.product', string='Pkg 1',
        compute='_calculate_packages', readonly=True)
    sec_pack_qty = fields.Float(
        string='# Pkg 2', compute='_calculate_packages',
        digits=dp.get_precision('Product Unit of Measure'), store=True)
    sec_pack_id = fields.Many2one(
        comodel_name='product.ul', string='Pkg 2')
