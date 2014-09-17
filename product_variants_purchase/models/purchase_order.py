# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _


class ProductAttributeValuePurchaseLine(models.Model):
    _name = 'purchase.order.line.attribute'

    purchase_line = fields.Many2one(comodel_name='purchase.order.line',
                                    string='Order line')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            domain="[('attribute_id', '=', attribute)]",
                            string='Value')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    type = fields.Selection([('product', 'Product'), ('variant', 'Variant')],
                            string='Type', default='variant')
    product_template = fields.Many2one(comodel_name='product.template',
                                       domain="[('attribute_line_ids', '!=',"
                                       " False)]",
                                       string='Product Template')
    product_attributes = fields.One2many('purchase.order.line.attribute',
                                         'purchase_line',
                                         string='Product attributes',
                                         copyable=True)

    @api.one
    @api.onchange('product_template')
    def onchange_product_template(self):
        product_attributes = []
        for attribute in self.product_template.attribute_line_ids:
            product_attributes.append({'attribute': attribute.attribute_id})
        self.product_attributes = product_attributes
        self.name = self.product_template.name

    @api.one
    def action_duplicate(self):
        self.copy()
        # Force reload of payment order view as a workaround for lp:1155525
        return {
            'name': _('Purchase order'),
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'purchase.order',
            'res_id': self.order_id.id,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_confirm(self):
        for line in self:
            if line.type == 'variant':
                product_obj = self.env['product.product']
                att_values_ids = [attr_line.value and attr_line.value.id or False
                                  for attr_line in line.product_attributes]
                domain = [('product_tmpl_id', '=', line.product_template.id)]
                for value in att_values_ids:
                    domain.append(('attribute_value_ids', '=', value))
                product = product_obj.search(domain)
                if not product:
                    product = product_obj.create(
                        {'product_tmpl_id': line.product_template.id,
                         'attribute_value_ids': [(6, 0, att_values_ids)]})
                line.write({'product_id': product.id})
        super(PurchaseOrderLine, self).action_confirm()

#     @api.one
#     def copy(self):
#         return super(PurchaseOrderLine, self).copy()
