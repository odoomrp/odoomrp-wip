# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.one
    @api.onchange('only_products_allowed')
    def onchange_only_products_allowed(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        product_obj = self.env['product.product']
        self.allowed_products = []
        allowed_products = []
        if self.only_products_allowed and self.partner_id:
            cond = [('type', '=', 'supplier'),
                    ('name', '=', self.partner_id.id)]
            supplierinfo_ids = supplierinfo_obj.search(cond)
            for line in supplierinfo_ids:
                if line.product_tmpl_id.purchase_ok:
                    cond = [('product_tmpl_id', '=', line.product_tmpl_id.id)]
                    products = product_obj.search(cond)
                    for product in products:
                        allowed_products.append(product.id)
        else:
            products = product_obj.search([])
            for product in products:
                if product.product_tmpl_id.purchase_ok:
                    allowed_products.append(product.id)
        self.allowed_products = [(6, 0, allowed_products)]
