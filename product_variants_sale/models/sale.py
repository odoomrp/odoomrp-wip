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
                                       string='Product Template')
    product_attributes = fields.One2many('sale.order.line.attribute',
                                         'sale_line',
                                         string='Product attributes')

    @api.one
    @api.onchange('product_template')
    def onchange_product_template(self):
        product_attributes = []
        for attribute in self.product_template.attribute_line_ids:
            product_attributes.append({'attribute': attribute.attribute_id})
        self.product_attributes = product_attributes


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_button_confirm(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                tmpl_id = line.product_template.id
                att_values = [attr_line.value and attr_line.value.id or False
                              for attr_line in line.product_attributes]
                domain = [('product_tmpl_id', '=', tmpl_id)]
                for value in att_values:
                    domain.append(('attribute_value_ids', '=', value))
                product_obj = self.pool['product.product']
                product_id = product_obj.search(cr, uid, domain,
                                                context=context)
                if not product_id:
                    product_id = product_obj.create(
                        cr, uid, {'product_tmpl_id': tmpl_id,
                                  'attribute_value_ids': [(6, 0,
                                                           att_values)]},
                        context=context)
                self.pool['sale.order.line'].write(cr, uid, line.id,
                                                   {'product_id': product_id},
                                                   context=context)
        return super(SaleOrder, self).action_button_confirm(cr, uid, ids,
                                                            context=context)
