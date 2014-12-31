# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    no_create_variants = fields.Boolean(
        string="Don't create variants automatically",
        help='This check disables the automatic creation of product variants '
             'for all the products of this category.', default=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    no_create_variants = fields.Selection(
        [('yes', 'Create them automatically'),
         ('no', "Don't create them automatically"),
         ('empty', 'Use the category value')],
        string='Variant creation', required=True, default='empty',
        help="This selection defines if variants for all attribute "
             "combinations are going to be created automatically at saving "
             "time.")

    def _get_product_attributes_dict(self):
        product_attributes = []
        for attribute in self.attribute_line_ids:
            product_attributes.append({'attribute': attribute.attribute_id.id})
        return product_attributes

    @api.multi
    def create_variant_ids(self):
        for tmpl in self:
            if ((tmpl.no_create_variants == 'empty' and
                    not tmpl.categ_id.no_create_variants) or
                    (tmpl.no_create_variants == 'no')):
                return super(ProductTemplate, self).create_variant_ids()
            else:
                return True

    @api.multi
    def action_open_attribute_prices(self):
        price_obj = self.env['product.attribute.price']
        for line in self.attribute_line_ids:
            for value in line.value_ids:
                prices = price_obj.search([('product_tmpl_id', '=', self.id),
                                           ('value_id', '=', value.id)])
                if not prices:
                    price_obj.create({
                        'product_tmpl_id': self.id,
                        'value_id': value.id,
                    })
        result = self._get_act_window_dict(
            'product_variants_no_automatic_creation.attribute_price_action')
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_product_attributes_values_dict(self):
        product_attributes = []
        for attr_value in self.attribute_value_ids:
            product_attributes.append({'attribute': attr_value.attribute_id.id,
                                       'value': attr_value.id})
        return product_attributes

    def _product_find(self, product_template, product_attributes):
        domain = []
        if product_template:
            domain.append(('product_tmpl_id', '=', product_template.id))
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    attribute_id = attr_line.get('attribute')
                    value_id = attr_line.get('value')
                else:
                    attribute_id = attr_line.attribute.id
                    value_id = attr_line.value.id
                if len(product_template.attribute_line_ids.search(
                        [('product_tmpl_id', '=', product_template.id),
                         ('attribute_id', '=',
                          attribute_id)]).value_ids) > 1:
                    domain.append(('attribute_value_ids', '=',
                                   value_id))
            return self.search(domain, limit=1) or False
        return False


class ProductAttributePrice(models.Model):
    _inherit = 'product.attribute.price'

    attribute = fields.Many2one(comodel_name='product.attribute',
                                related='value_id.attribute_id')
