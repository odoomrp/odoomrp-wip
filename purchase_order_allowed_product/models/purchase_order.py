# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    only_products_allowed = fields.Boolean(
        string="Use only allowed products in purchase")
    allowed_products = fields.Many2many(
        comodel_name='product.product',
        string='Allowed products')

    @api.multi
    def onchange_partner_id(self, partner_id):
        partner_obj = self.env['res.partner']
        result = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        partner = partner_obj.browse(partner_id)
        value = result['value']
        value['only_products_allowed'] = partner.purchase_only_allowed
        result['value'] = value
        return result

    @api.one
    @api.onchange('only_products_allowed')
    def onchange_only_products_allowed(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        product_obj = self.env['product.product']
        allowed_products = []
        products = product_obj.search([])
        for product in products:
            if product.product_tmpl_id.purchase_ok:
                allowed_products.append(product.id)
        self.allowed_products = [(6, 0, allowed_products)]
        allowed_products = []
        if self.only_products_allowed and self.partner_id:
            cond = self._prepare_allowed_product_domain()
            supplierinfo_ids = supplierinfo_obj.search(cond)
            for line in supplierinfo_ids:
                if line.product_tmpl_id.purchase_ok:
                    cond = [('product_tmpl_id', '=', line.product_tmpl_id.id)]
                    products = product_obj.search(cond)
                    allowed_products.extend(products.ids)
            self.allowed_products = [(6, 0, allowed_products)]

    def _prepare_allowed_product_domain(self):
        return [('name', '=', self.partner_id.id)]
