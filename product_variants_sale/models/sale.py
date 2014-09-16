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


class ProductAttributeValueSaleLine(models.Model):
    _name = 'sale.order.line.attribute'

    sale_line = fields.Many2one(comodel_name='sale.order.line',
                                string='Order line')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            domain="[('attribute_id', '=', attribute)]",
                            string='Value')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    type = fields.Selection([('product', 'Product'), ('variant', 'Variant')],
                            string='Type', default='variant')
    product_template = fields.Many2one(comodel_name='product.template',
                                       domain="[('attribute_line_ids', '!=',"
                                       " False)]",
                                       string='Product Template')
    product_attributes = fields.One2many('sale.order.line.attribute',
                                         'sale_line',
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
            'name': _('Sale order'),
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def button_confirm(self):
        for line in self:
            if not line.product_id:
                tmpl_id = line.product_template.id
                if not tmpl_id:
                    tmpl_id = line.product_id.product_tmpl_id.id
                att_values = [attr_line.value and attr_line.value.id or False
                              for attr_line in line.product_attributes]
                domain = [('product_tmpl_id', '=', tmpl_id)]
                for value in att_values:
                    domain.append(('attribute_value_ids', '=', value))
                    product_obj = self.env['product.product']
                product = product_obj.search(domain)
                if not product:
                    product = product_obj.create(
                        {'product_tmpl_id': tmpl_id,
                         'attribute_value_ids': [(6, 0, att_values)]})
                line.write({'product_id': product.id})
            elif not line.product_template:
                line.write({'product_template': line.product_id.product_tmpl_id.id})
        super(SaleOrderLine, self).button_confirm()

    @api.multi
    def write(self, values):
        if values.get('product_id') and not values.get('product_template'):
            product_obj = self.env['product.product']
            product_template = product_obj.browse(
                values['product_id']).product_tmpl_id
            values['product_template'] = product_template.id
        super(SaleOrderLine, self).write(values)

#     @api.one
#     def copy(self):
#         return super(SaleOrderLine, self).copy()
