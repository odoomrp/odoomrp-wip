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

from openerp import models, fields, api, _


class ProductAttributeValueSaleLine(models.Model):
    _name = 'sale.order.line.attribute'

    @api.one
    @api.depends('attribute', 'sale_line.product_template',
                 'sale_line.product_template.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.sale_line.product_template.attribute_line_ids:
            if attr_line.attribute_id.id == self.attribute.id:
                attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()

    sale_line = fields.Many2one(
        comodel_name='sale.order.line', string='Order line')
    attribute = fields.Many2one(
        comodel_name='product.attribute', string='Attribute')
    value = fields.Many2one(
        comodel_name='product.attribute.value', string='Value',
        domain="[('id', 'in', possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product Template')
    product_attributes = fields.One2many(
        comodel_name='sale.order.line.attribute', inverse_name='sale_line',
        string='Product attributes', copyable=True)

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        for line in self:
            line.name = line.product_template.name
            product_attributes = []
            if not line.product_template.attribute_line_ids:
                line.product_id = (
                    line.product_template.product_variant_ids and
                    line.product_template.product_variant_ids[0])
            else:
                line.product_id = False
            line.product_attributes = (
                self.product_template._get_product_attributes())
        return {'domain': {'product_id': [('product_tmpl_id', '=',
                                           self.product_template.id)]}}

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        description = self.product_template.name
        for attr_line in self.product_attributes:
            if attr_line.value:
                description += _('\n%s: %s') % (attr_line.attribute.name,
                                                attr_line.value.name)
        self.product_id = product_obj._product_find(self.product_template,
                                                    self.product_attributes)
        self.name = description

    @api.multi
    def action_duplicate(self):
        self.ensure_one()
        self.copy()
        # Force reload of the view as a workaround for lp:1155525
        return {
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
                product_obj = self.env['product.product']
                att_values_ids = [attr_line.value and attr_line.value.id
                                  or False
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
        super(SaleOrderLine, self).button_confirm()
