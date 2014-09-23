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

    @api.one
    @api.onchange('product_id')
    def onchange_product_product(self):
        self.product_template = self.product_id.product_tmpl_id

    @api.one
    @api.onchange('product_template')
    def onchange_product_template(self):
        product_attributes = []
        for attribute in self.product_template.attribute_line_ids:
            product_attributes.append({'attribute': attribute.attribute_id})
        self.product_attributes = product_attributes


class MrpProductionAttribute(models.Model):
    _name = 'mrp.production.attribute'

    mrp_production = fields.Many2one(comodel_name='mrp.production.attribute',
                                     string='Manufacturing Order')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            domain="[('attribute_id', '=', attribute)]",
                            string='Value')


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

    @api.one
    @api.onchange('product_template')
    def onchange_product_template(self):
        product_attributes = []
        for attribute in self.product_template.attribute_line_ids:
            product_attributes.append({'attribute': attribute.attribute_id})
        self.product_attributes = product_attributes
