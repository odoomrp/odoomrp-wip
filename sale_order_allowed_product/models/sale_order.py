# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    only_allowed_products = fields.Boolean(
        string="Use only allowed products",
        help="If checked, you will only be able to select products that have "
             "this customer added to their customer list.")
    allowed_tmpl_ids = fields.Many2many(
        comodel_name='product.template', string='Allowed templates',
        compute='_compute_allowed')
    allowed_product_ids = fields.Many2many(
        comodel_name='product.product', string='Allowed products',
        compute='_compute_allowed')

    @api.multi
    def onchange_partner_id(self, partner_id):
        result = super(SaleOrder, self).onchange_partner_id(partner_id)
        partner = self.env['res.partner'].browse(partner_id)
        result['value']['only_allowed_products'] =\
            partner.commercial_partner_id.sale_only_allowed
        return result

    @api.depends('only_allowed_products', 'partner_id')
    def _compute_allowed(self):
        product_obj = self.env['product.template']
        for order in self:
            if order.only_allowed_products and order.partner_id:
                suppinfo = self.env['product.supplierinfo'].search(
                    [('type', '=', 'customer'),
                     ('name', 'in', (order.partner_id.commercial_partner_id.id,
                                     order.partner_id.id))])
                allowed_tmpl_ids = suppinfo.mapped('product_tmpl_id')
            else:
                allowed_tmpl_ids = product_obj.search(
                    [('sale_ok', '=', True)])
            order.allowed_tmpl_ids = allowed_tmpl_ids.filtered('sale_ok')
            order.allowed_product_ids =\
                order.mapped(
                    'allowed_tmpl_ids.product_variant_ids').filtered('sale_ok')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Inject the domain here to avoid conflicts with other modules.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        for field in res['fields']:
            if field == 'order_line' and 'views' in res['fields'][field]:
                if 'tree' in res['fields'][field]['views']:
                    for line_field in res['fields'][field]['views']['tree']['fields']:
                        if line_field == 'product_id':
                            print res['fields'][field]['views']['tree']['fields'][line_field]['domain']
                        elif line_field == 'product_tmpl_id':
                            print res['fields'][field]['views']['tree']['fields'][line_field]['domain']
                if 'form' in res['fields'][field]['views']:
                    for line_field in res['fields'][field]['views']['tree']['fields']:
                        if line_field == 'product_id':
                            print res['fields'][field]['views']['tree']['fields'][line_field]['domain']
                        elif line_field == 'product_tmpl_id':
                            print res['fields'][field]['views']['tree']['fields'][line_field]['domain']
#             if field == 'product_id' and self.allowed_product_ids:
#                 res['fields'][field]['domain'] =\
#                     "[('id', 'in', parent.allowed_product_ids[0][2])]"
#             elif field == 'product_tmpl_id' and self.allowed_tmpl_ids:
#                 res['fields'][field]['domain'] =\
#                     "[('id', 'in', parent.allowed_tmpl_ids[0][2])]"
        return res
