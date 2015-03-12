
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import fields, models, api
from itertools import product


class ReassignProducts(models.TransientModel):
    _name = "reassign.products"
    _rec_name = "products"
    products = fields.One2many('reassign.product.lines',
                               'reassign', string='Attributes Products')

    @api.multi
    def _product_by_variants(self, variants, products):
        set_var_ids = set(variants)
        for product in products:
            if set(product.attribute_value_ids.ids) == set_var_ids:
                return product.id

    @api.model
    def default_get(self, var_fields):
        lines = {}
        template = self.env['product.template'].browse(
            self.env.context['active_id'])
        values = product(*map(lambda x: x.value_ids.ids,
                              template.attribute_line_ids))
        val_list = list(values)
        products = template.product_variant_ids
        lines = []
        for vals in val_list:
            val_product = self._product_by_variants(vals, products)
            lines.append((0, 0, {'attributes': [(6, 0, list(vals))],
                                 'exists': val_product and True,
                                 'product': val_product
                                 }))
        return {'products': lines}

    @api.multi
    def reassign(self):
        for line in self.products:
            if line.product:
                template = line.product.product_tmpl_id
                line.product.write(
                    {'attribute_value_ids': [(6, 0, line.attributes.ids)],
                     'product_tmpl_id': self.env.context['active_id']})
                if len(template.product_variant_ids.ids) == 0:
                    template.unlink()


class ReassignProductLines(models.TransientModel):
    _name = "reassign.product.lines"

    attributes = fields.Many2many('product.attribute.value',
                                  string="Attributes")
    reassign = fields.Many2one(comodel_name='reassign.products',
                               string='Reassign Wizard')
    product = fields.Many2one(comodel_name='product.product',
                              string='Product')
    exists = fields.Boolean(string="Exists")
