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

from openerp import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    no_create_variants = fields.Boolean(
        string="Don't create variants automatically",
        help='This check disables the automatic creation of product variants '
             'for all the products of this category.', default=True)

    @api.multi
    @api.onchange('no_create_variants')
    def onchange_no_create_variants(self):
        self.ensure_one()
        if not self._origin:
            return {}
        return {'warning': {'title': _('Change warning!'),
                            'message': _('Changing this parameter may cause'
                                         ' automatic variants creation')}}

    @api.multi
    def write(self, values):
        res = super(ProductCategory, self).write(values)
        if ('no_create_variants' in values and
                not values.get('no_create_variants')):
            self.env['product.template'].search(
                [('categ_id', '=', self.id),
                 ('no_create_variants', '=', 'empty')]).create_variant_ids()
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    no_create_variants = fields.Selection(
        [('yes', "Don't create them automatically"),
         ('no', "Create them automatically"),
         ('empty', 'Use the category value')],
        string='Variant creation', required=True, default='empty',
        help="This selection defines if variants for all attribute "
             "combinations are going to be created automatically at saving "
             "time.")

    @api.multi
    @api.onchange('no_create_variants')
    def onchange_no_create_variants(self):
        self.ensure_one()
        if not self._origin:
            return {}
        return {'warning': {'title': _('Change warning!'),
                            'message': _('Changing this parameter may cause'
                                         ' automatic variants creation')}}

    @api.multi
    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if 'no_create_variants' in values:
            self.create_variant_ids()
        return res

    def _get_product_attributes_dict(self):
        return self.attribute_line_ids.mapped(
            lambda x: {'attribute': x.attribute_id.id})

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

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        temp = super(models.Model, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        # Make the other search
        temp += super(ProductTemplate, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        # Merge both results
        res = []
        keys = []
        for val in temp:
            if val[0] not in keys:
                res.append(val)
                keys.append(val[0])
                if len(res) >= limit:
                    break
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_product_attributes_values_dict(self):
        # Retrieve first the attributes from template to preserve order
        res = self.product_tmpl_id._get_product_attributes_dict()
        for val in res:
            value = self.attribute_value_ids.filtered(
                lambda x: x.attribute_id.id == val['attribute'])
            val['value'] = value.id
        return res

    def _get_product_attributes_values_text(self):
        description = self.attribute_value_ids.mapped(
            lambda x: "%s: %s" % (x.attribute_id.name, x.name))
        return "%s\n%s" % (self.product_tmpl_id.name, "\n".join(description))

    def _product_find(self, product_template, product_attributes):
        domain = []
        if product_template:
            domain.append(('product_tmpl_id', '=', product_template.id))
            attr_values = []
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    attribute_id = attr_line.get('attribute')
                    value_id = attr_line.get('value')
                else:
                    attribute_id = attr_line.attribute.id
                    value_id = attr_line.value.id
                if value_id and len(product_template.attribute_line_ids.search(
                        [('product_tmpl_id', '=', product_template.id),
                         ('attribute_id', '=', attribute_id)]).value_ids) > 1:
                    domain.append(('attribute_value_ids', '=', value_id))
                    attr_values.append(value_id)
            products = self.search(domain)
            # Filter the product with the exact number of attributes values
            for product in products:
                if len(product.attribute_value_ids) == len(attr_values):
                    return product
        return False


class ProductAttributeLine(models.Model):
    _inherit = 'product.attribute.line'

    _sql_constraints = [
        ('product_attribute_uniq', 'unique(product_tmpl_id, attribute_id)',
         'The attribute already exists for this product')
    ]


class ProductAttributePrice(models.Model):
    _inherit = 'product.attribute.price'

    attribute = fields.Many2one(comodel_name='product.attribute',
                                related='value_id.attribute_id')
