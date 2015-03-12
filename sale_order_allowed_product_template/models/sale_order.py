# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allowed_templates = fields.Many2many(
        comodel_name='product.template', string='Allowed product templates')

    @api.one
    @api.onchange('only_allowed_products')
    def onchange_only_allowed_products(self):
        template_obj = self.env['product.template']
        self.allowed_templates = template_obj.search([('sale_ok', '=', True)])
        if self.only_allowed_products and self.partner_id:
            supplierinfos = self.env['product.supplierinfo'].search(
                [('type', '=', 'customer'),
                 ('name', 'in', (self.partner_id.commercial_partner_id.id,
                                 self.partner_id.id))])
            self.allowed_templates = template_obj.search(
                [('id', 'in', [x.product_tmpl_id.id for x in supplierinfos])])
