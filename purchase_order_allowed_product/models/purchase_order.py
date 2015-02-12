# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    only_allowed_products = fields.Boolean(
        string="Use only allowed products",
        help="If checked, you will only be able to select products that can be"
             " supplied by this supplier.")
    allowed_products = fields.Many2many(
        comodel_name='product.product', string='Allowed products')

    @api.multi
    def onchange_partner_id(self, partner_id):
        result = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        partner = self.env['res.partner'].browse(partner_id)
        result['value']['only_allowed_products'] = (
            partner.commercial_partner_id.purchase_only_allowed)
        return result

    @api.one
    @api.onchange('only_allowed_products')
    def onchange_only_allowed_products(self):
        product_obj = self.env['product.product']
        self.allowed_products = product_obj.search(
            [('purchase_ok', '=', True)])
        if self.only_allowed_products and self.partner_id:
            cond = self._prepare_allowed_product_domain()
            supplierinfos = self.env['product.supplierinfo'].search(cond)
            self.allowed_products = product_obj.search(
                [('product_tmpl_id', 'in',
                  [x.product_tmpl_id.id for x in supplierinfos])])

    def _prepare_allowed_product_domain(self):
        return [('name', 'in', (self.partner_id.commercial_partner_id.id,
                                self.partner_id.id))]
