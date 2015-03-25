
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
from itertools import product as iter_product


class ReassignProducts(models.TransientModel):
    _name = "reassign.products"

    products = fields.One2many(
        comodel_name='reassign.product.lines',
        inverse_name='wizard', string='Products by attributes')

    @api.multi
    def _product_by_variants(self, variants, products):
        set_var_ids = set(variants)
        for product in products:
            if set(product.attribute_value_ids.ids) == set_var_ids:
                return product.id
        return False

    @api.model
    def default_get(self, var_fields):
        template = self.env['product.template'].browse(
            self.env.context['active_id'])
        values = iter_product(*map(lambda x: x.value_ids.ids,
                                   template.attribute_line_ids))
        val_list = list(values)
        products = template.product_variant_ids
        lines = []
        for vals in val_list:
            line_vals = {
                'attributes': [(6, 0, list(vals))],
                'product': self._product_by_variants(vals, products),
            }
            line_vals['old_product'] = line_vals['product']
            lines.append((0, 0, line_vals))
        return {'products': lines}

    @api.multi
    def reassign(self):
        template_id = self.env.context['active_id']
        for line in self.products:
            if line.product:
                old_template = line.product.product_tmpl_id
                if old_template.id == template_id:
                    continue
                if line.old_product:
                    line.old_product.unlink()
                line.product.write(
                    {'attribute_value_ids': [(6, 0, line.attributes.ids)],
                     'product_tmpl_id': template_id})
                if not old_template.product_variant_ids:
                    old_template.unlink()
        return True


class ReassignProductLines(models.TransientModel):
    _name = "reassign.product.lines"

    wizard = fields.Many2one(
        comodel_name='reassign.products', string='Reassign Wizard',
        required=True)
    attributes = fields.Many2many(
        'product.attribute.value', string="Attributes")
    old_product = fields.Many2one(
        comodel_name='product.product', string='Product')
    product = fields.Many2one(
        comodel_name='product.product', string='Product')
