# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    only_products_allowed = fields.Boolean(
        string="Use only allowed products in sale")
    allowed_products = fields.Many2many(
        comodel_name='product.product',
        string='Allowed products')

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool['res.partner']
        result = super(SaleOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        value = result['value']
        value['only_products_allowed'] = (
            partner.sale_only_allowed)
        return result

    @api.one
    @api.onchange('only_products_allowed')
    def onchange_only_products_allowed(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        product_obj = self.env['product.product']
        allowed_products = []
        products = product_obj.search([])
        for product in products:
            if product.product_tmpl_id.sale_ok:
                allowed_products.append(product.id)
        self.allowed_products = allowed_products
        allowed_products = []
        if self.only_products_allowed and self.partner_id:
            cond = [('type', '=', 'customer'),
                    ('name', '=', self.partner_id.id)]
            supplierinfo_ids = supplierinfo_obj.search(cond)
            for line in supplierinfo_ids:
                if line.product_tmpl_id.sale_ok:
                    cond = [('product_tmpl_id', '=', line.product_tmpl_id.id)]
                    products = product_obj.search(cond)
                    if products:
                        allowed_products.extend(products.ids)
            self.allowed_products = [(6, 0, allowed_products)]
