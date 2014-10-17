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


class MrpBomAttribute(models.Model):
    _name = 'mrp.bom.attribute'

    mrp_bom_line = fields.Many2one(comodel_name='mrp.bom.line', string='BoM')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            domain="[('attribute_id', '=', attribute)]",
                            string='Value')


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one(required=False)
    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product')
    product_attributes = fields.One2many(comodel_name='mrp.bom.attribute',
                                         inverse_name='mrp_bom_line',
                                         string='Product attributes',
                                         copyable=True)
    attribute_value_ids = fields.Many2many(
        domain="[('id','in',possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')

    @api.one
    @api.depends('bom_id.product_tmpl_id')
    def _get_possible_attribute_values(self):
        domain = []
        for attr_line in self.bom_id.product_tmpl_id.attribute_line_ids:
            for attr_value in attr_line.value_ids:
                domain.append(attr_value.id)
        self.possible_values = domain

    @api.one
    @api.onchange('product_id')
    def onchange_product_product(self):
        self.product_template = self.product_id.product_tmpl_id

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        if self.product_template:
            product_attributes = []
            for attribute in self.product_template.attribute_line_ids:
                product_attributes.append({'attribute':
                                           attribute.attribute_id})
            self.product_attributes = product_attributes
            return {'domain': {'product_id': [('product_tmpl_id', '=',
                                               self.product_template.id)]}}
        return {'domain': {'product_id': []}}


class MrpProductionAttribute(models.Model):
    _name = 'mrp.production.attribute'

    mrp_production = fields.Many2one(comodel_name='mrp.production',
                                     string='Manufacturing Order')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            string='Value',
                            domain="[('attribute_id','=',attribute),"
                            "('id','in',possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')

    @api.one
    @api.depends('mrp_production.product_template')
    def _get_possible_attribute_values(self):
        domain = []
        for attr_line in self.mrp_production.product_template.attribute_line_ids:
            for attr_value in attr_line.value_ids:
                domain.append(attr_value.id)
        self.possible_values = domain


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_id = fields.Many2one(required=False)
    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product', readonly=True,
                                       states={'draft': [('readonly', False)]})
    product_attributes = fields.One2many(
        comodel_name='mrp.production.attribute', inverse_name='mrp_production',
        string='Product attributes', copyable=True, readonly=True,
        states={'draft': [('readonly', False)]},)

    def product_id_change(self, cr, uid, ids, product_id, product_qty=0,
                          context=None):
        result = super(MrpProduction, self).product_id_change(
            cr, uid, ids, product_id, product_qty=product_qty, context=context)
        product_obj = self.pool['product.product']
        product = product_obj.browse(cr, uid, product_id, context=context)
        result['value'].update(
            {'product_template': product.product_tmpl_id.id})
        return result

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        for mo in self:
            product_attributes = []
            if not mo.product_template.attribute_line_ids:
                mo.product_id = (
                    mo.product_template.product_variant_ids and
                    mo.product_template.product_variant_ids[0])
            for attribute in mo.product_template.attribute_line_ids:
                product_attributes.append({'attribute':
                                           attribute.attribute_id})
            mo.product_attributes = product_attributes
            return {'domain': {'product_id':
                               [('product_tmpl_id', '=',
                                 mo.product_template.id)]}}

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        if not self.product_id:
            product_obj = self.env['product.product']
            att_values_ids = [attr_line.value and attr_line.value.id
                              or False
                              for attr_line in self.product_attributes]
            domain = [('product_tmpl_id', '=', self.product_template.id)]
            for value in att_values_ids:
                domain.append(('attribute_value_ids', '=', value))
            self.product_id = product_obj.search(domain, limit=1)
