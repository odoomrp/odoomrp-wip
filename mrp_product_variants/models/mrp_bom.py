# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from itertools import groupby
from operator import attrgetter


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one(required=False)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product')
    attribute_value_ids = fields.Many2many(
        domain="[('id', 'in', possible_value_ids[0][2])]")
    possible_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_compute_possible_attribute_values')
    product_uom_category = fields.Many2one(
        comodel_name='product.uom.categ', string='UoM category',
        compute="_compute_product_category")
    product_uom = fields.Many2one(
        domain="[('category_id', '=', product_uom_category)]")

    @api.depends('product_id', 'product_tmpl_id')
    def _compute_product_category(self):
        for line in self:
            line.product_uom_category = (
                line.product_id.uom_id.category_id or
                line.product_tmpl_id.uom_id.category_id)

    @api.depends('bom_id.product_tmpl_id',
                 'bom_id.product_tmpl_id.attribute_line_ids')
    def _compute_possible_attribute_values(self):
        for line in self:
            attr_values = self.env['product.attribute.value']
            for attr_line in line.bom_id.product_tmpl_id.attribute_line_ids:
                attr_values |= attr_line.value_ids
            line.possible_value_ids = attr_values.sorted()

    @api.multi
    def onchange_product_id(self, product_id, product_qty=0):
        res = super(MrpBomLine, self).onchange_product_id(
            product_id, product_qty=product_qty)
        if product_id:
            product = self.env['product.product'].browse(product_id)
            res['value']['product_tmpl_id'] = product.product_tmpl_id.id
        return res

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_uom = (self.product_id.uom_id or
                                self.product_tmpl_id.uom_id)
            return {'domain': {'product_id': [('product_tmpl_id', '=',
                                               self.product_tmpl_id.id)]}}
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
                for attr_value in production.product_attribute_ids:
                    production_attr_values.append(attr_value.value_id.id)
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
                    product_tmpl_id=bom_line.product_tmpl_id.id,
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
            tmpl_id = bom_line.product_tmpl_id
            res['name'] = tmpl_id.name
            res['product_tmpl_id'] = tmpl_id.id
            production = self.env.context.get('production')
            if not production and\
                    self.env.context.get('active_model') == 'mrp.production':
                production = self.env['mrp.production'].browse(
                    self.env.context.get('active_id'))
            self.env.context.get('active_id')
            product_attribute_ids = (
                tmpl_id._get_product_attribute_ids_inherit_dict(
                    production.product_attribute_ids))
            comp_product = self.env['product.product']._product_find(
                tmpl_id, product_attribute_ids)
            res['product_id'] = comp_product and comp_product.id
        else:
            res['product_tmpl_id'] = bom_line.product_id.product_tmpl_id.id
            product_attribute_ids = (
                bom_line.product_id._get_product_attributes_values_dict())
        res['product_attribute_ids'] = map(
            lambda x: (0, 0, x), product_attribute_ids)
        for val in res['product_attribute_ids']:
            val = val[2]
            val['product_tmpl_id'] = res['product_tmpl_id']
            val['owner_model'] = 'mrp.production.product.line'
        return res

    @api.model
    def _get_bom_product_name(self, bom_line):
        if not bom_line.product_id:
            return bom_line.product_tmpl_id.name_get()[0][1]
        else:
            return super(MrpBom, self)._get_bom_product_name(bom_line)
