# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _
from itertools import product


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('attribute_line_ids')
    def check_circular_dependency(self):
        for attr_line in self.attribute_line_ids:
            pred_lines = self.attribute_line_ids.filtered(
                lambda x: attr_line.attribute_id in x.predecessors)
            if attr_line.predecessors in pred_lines.mapped(
                    'attribute_id'):
                raise exceptions.Warning('There is a circular dependency')


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"

    @api.one
    @api.depends('product_tmpl_id.attribute_line_ids')
    def _get_possible_attributes(self):
        attrs = self.env['product.attribute']
        for attr_line in self.product_tmpl_id.attribute_line_ids:
            if attr_line.attribute_id != self.attribute_id:
                attrs |= attr_line.attribute_id
        self.possible_values = attrs.sorted()

    @api.constrains('predecessors', 'initial')
    def check_initial_has_predecessors(self):
        if self.initial and self.predecessors:
            raise exceptions.Warning('initial attribute cant content '
                                     'predecessors')

    @api.constrains('predecessors', 'predecessors_constraint')
    def check_predecessors_values(self):
        if self.predecessors_constraint - self.possible_predecessor_values:
            raise exceptions.Warning('There are values that not longer exist')

    @api.one
    @api.depends('predecessors')
    def _get_possible_values(self):
        if self.predecessors:
            values = self.env['product.attribute.value'].search(
                [('attribute_id', 'in', self.predecessors.ids)])
            self.possible_predecessor_values = values

    initial = fields.Boolean(string='Initial')
    predecessors = fields.Many2many(
        comodel_name='product.attribute',
        relation='attribute_predecessors_rel',
        column1='attribute_line',
        column2='product_attribute',
        domain="[('id', 'in', possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute',
        relation='attribute_possible_values',
        column1='attribute_line',
        column2='product_attribute',
        compute='_get_possible_attributes', readonly=True)
    predecessors_constraint = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='predecessors_constraint_rel',
        column1='line_id',
        column2='value_id',
        domain="[('id', 'in', possible_predecessor_values[0][2])]")
    possible_predecessor_values = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='predecessors_constraint_possible_values_rel',
        column1='line_id',
        column2='value_id', compute='_get_possible_values', readonly=True)
    value_constraints = fields.One2many(comodel_name='value.constraint',
                                        inverse_name='attribute_line')


class ValueConstraint(models.Model):
    _name = 'value.constraint'
    _rec_name = 'attribute_line'

    # @api.one
    # @api.depends('attribute_line.predecessors_constraint')
    # def _get_possible_predecessors_attribute_values(self):
    #     self.possible_values = self.attribute_line.predecessors_constraint
    #
    # @api.one
    # @api.depends('attribute_line.value_ids')
    # def _get_possible_attribute_values(self):
    #     self.possible_allowed_values = self.attribute_line.value_ids

    predecessor_values = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='predecessors_values_rel',
        column1='value_constraint_id',
        column2='attribute_value_id',
        )
    # possible_values = fields.Many2many(
    #     comodel_name='product.attribute.value',
    #     compute='_get_possible_attribute_values', readonly=True)
    # possible_values = fields.Many2many(
    #     comodel_name='product.attribute.value',
    #     related='attribute_line.predecessors_constraint', readonly=True)
    allowed_values = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='possible_values_rel',
        column1='value_constraint_id',
        column2='attribute_value_id',
        )
    # possible_allowed_values = fields.Many2many(
    #     comodel_name='product.attribute.value', readonly=True)
    attribute_line = fields.Many2one(comodel_name='product.attribute.line')