# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, fields, models
from openerp.tools import ustr


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
        product_tmpl_id field will only be present when sale_order_variants
        is installed.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != 'form':
            return res  # pragma: no cover
        domain_dict = {
            'product_id': "('id', 'in', parent.allowed_product_ids[0][2]), ",
            'product_tmpl_id': "('id', 'in', parent.allowed_tmpl_ids[0][2]), ",
        }
        if 'order_line' not in res['fields']:
            return res  # pragma: no cover
        line_field = res['fields']['order_line']
        for view_type, view in line_field['views'].iteritems():
            if view_type not in ('tree', 'form'):
                continue  # pragma: no cover
            for field_name, domain_field in domain_dict.iteritems():
                if field_name not in view['fields']:
                    continue  # pragma: no cover
                field = view['fields'][field_name]
                domain = ustr(field.get('domain', "[]"))
                field['domain'] = domain[:1] + domain_field + domain[1:]
        return res
