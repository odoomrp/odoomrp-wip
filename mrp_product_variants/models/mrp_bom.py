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
from itertools import groupby
from operator import attrgetter


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one(required=False)
    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product')
    attribute_value_ids = fields.Many2many(
        domain="[('id', 'in', possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')

    @api.one
    @api.depends('product_id', 'product_template')
    def _get_product_category(self):
        self.product_uom_category = (self.product_id.uom_id.category_id or
                                     self.product_template.uom_id.category_id)

    product_uom_category = fields.Many2one(
        comodel_name='product.uom.categ', string='UoM category',
        compute="_get_product_category")
    product_uom = fields.Many2one(
        domain="[('category_id', '=', product_uom_category)]")

    @api.one
    @api.depends('bom_id.product_tmpl_id',
                 'bom_id.product_tmpl_id.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.bom_id.product_tmpl_id.attribute_line_ids:
            attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()

    @api.multi
    def onchange_product_id(self, product_id, product_qty=0):
        res = super(MrpBomLine, self).onchange_product_id(
            product_id, product_qty=product_qty)
        if product_id:
            product = self.env['product.product'].browse(product_id)
            res['value']['product_template'] = product.product_tmpl_id.id
        return res

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        if self.product_template:
            self.product_uom = (self.product_id.uom_id or
                                self.product_template.uom_id)
            return {'domain': {'product_id': [('product_tmpl_id', '=',
                                               self.product_template.id)]}}
        return {'domain': {'product_id': []}}


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _check_product_suitable(self, check_attribs, component_attribs):
        """ Check if component is suitable for given attributes
        @param check_attribs: Attribute id list
        @param component_attribs: Component defined attributes to check
        @return: Component validity
        """
        getattr = attrgetter('attribute_id')
        for key, group in groupby(component_attribs, getattr):
            if not set(check_attribs).intersection([x.id for x in group]):
                return False
        return True

    def _skip_bom_line(self, line, product):
        today = fields.Date.context_today(self)
        if (line.date_start and
                line.date_start > today or
                line.date_stop and (line.date_stop < today)):
            return True
        # all bom_line_id variant values must be in the product
        if line.attribute_value_ids:
            production_attr_values = []
            if not product and self.env.context.get('production'):
                production = self.env.context['production']
                for attr_value in production.product_attributes:
                    production_attr_values.append(attr_value.value.id)
                if not self._check_product_suitable(
                        production_attr_values,
                        line.attribute_value_ids):
                    return True
            elif not product or not self._check_product_suitable(
                    product.attribute_value_ids.ids,
                    line.attribute_value_ids):
                return True
        return False

    @api.model
    def _bom_find_prepare(self, bom_line, properties=None):
        if not bom_line.product_id:
            if not bom_line.type != "phantom":
                return self._bom_find(
                    product_tmpl_id=bom_line.product_template.id,
                    properties=properties)
            else:
                return False
        return super(MrpBom, self)._bom_find_prepare(
            bom_line, properties=properties)

    @api.model
    def _prepare_consume_line(self, bom_line, quantity, factor=1):
        res = super(MrpBom, self)._prepare_consume_line(
            bom_line, quantity, factor=factor)
        if not bom_line.product_id:
            res['name'] = bom_line.product_template.name
            res['product_template'] = bom_line.product_template.id
            production = self.env.context['production']
            product_attributes = (
                bom_line.product_template._get_product_attributes_inherit_dict(
                    production.product_attributes))
            comp_product = self.env['product.product']._product_find(
                bom_line.product_template, product_attributes)
            res['product_id'] = comp_product and comp_product.id
        else:
            res['product_template'] = bom_line.product_id.product_tmpl_id.id
            product_attributes = (
                bom_line.product_id._get_product_attributes_values_dict())
        res['product_attributes'] = map(
            lambda x: (0, 0, x), product_attributes)
        return res

    @api.model
    def _get_bom_product_name(self, bom_line):
        if not bom_line.product_id:
            return bom_line.product_template.name_get()[0][1]
        else:
            return super(MrpBom, self)._get_bom_product_name(bom_line)
