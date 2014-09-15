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
            tmpl_id = line.product_template.id
            att_values = [attr_line.value and attr_line.value.id or False
                          for attr_line in line.product_attributes]
            domain = [('product_tmpl_id', '=', tmpl_id)]
            for value in att_values:
                domain.append(('attribute_value_ids', '=', value))
            product_obj = self.pool['product.product']
            product_id = product_obj.search(self.env.cr, self.env.uid, domain,
                                            context=self.env.context)
            if not product_id:
                product_id = product_obj.create(
                    self.env.cr, self.env.uid,
                    {'product_tmpl_id': tmpl_id,
                     'attribute_value_ids': [(6, 0, att_values)]},
                    context=self.env.context)
            line.write({'product_id': product_id})
        super(PurchaseOrderLine, self).action_confirm()

    @api.multi
    def write(self, values):
        if values.get('product_id') and not values.get('product_template'):
            product_obj = self.pool['product.product']
            product_template = product_obj.read(
                self.env.cr, self.env.uid, values['product_id'],
                ['product_tmpl_id'], context=self.env.context)
            values['product_template'] = product_template['id']
        super(PurchaseOrderLine, self).write(values)

#     @api.one
#     def copy(self):
#         return super(PurchaseOrderLine, self).copy()
