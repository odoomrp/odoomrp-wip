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

import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, exceptions, tools, _
from openerp.addons.product import _common


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
    # attribute_value_ids = fields.Many2many(
    #     domain="[('id','in',possible_values[0][2])]")
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


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        """ Finds Products and Work Centers for related BoM for manufacturing
        order.
        @param bom: BoM of particular product template.
        @param product: Select a particular variant of the BoM. If False use
                        BoM without variants.
        @param factor: Factor represents the quantity, but in UoM of the BoM,
                        taking into account the numbers produced by the BoM
        @param properties: A List of properties Ids.
        @param level: Depth level to find BoM lines starts from 10.
        @param previous_products: List of product previously use by bom explore
                        to avoid recursion
        @param master_bom: When recursion, used to display the name of the
                        master bom
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        uom_obj = self.env["product.uom"]
        routing_obj = self.env['mrp.routing']
        master_bom = master_bom or bom

        def _factor(factor, product_efficiency, product_rounding):
            factor = factor / (product_efficiency or 1.0)
            factor = _common.ceiling(factor, product_rounding)
            if factor < product_rounding:
                factor = product_rounding
            return factor

        factor = _factor(factor, bom.product_efficiency, bom.product_rounding)

        result = []
        result2 = []

        routing = ((routing_id and routing_obj.browse(routing_id)) or
                   bom.routing_id or False)
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                mult = (d + (m and 1.0 or 0.0))
                cycle = mult * wc_use.cycle_nbr
                result2.append({
                    'name': (tools.ustr(wc_use.name) + ' - ' +
                             tools.ustr(bom.product_tmpl_id.name_get()[0][1])),
                    'workcenter_id': wc.id,
                    'sequence': level + (wc_use.sequence or 0),
                    'cycle': cycle,
                    'hour': float(wc_use.hour_nbr * mult +
                                  ((wc.time_start or 0.0) +
                                   (wc.time_stop or 0.0) + cycle *
                                   (wc.time_cycle or 0.0)) *
                                  (wc.time_efficiency or 1.0)),
                })

        for bom_line_id in bom.bom_line_ids:
            if bom_line_id.date_start and \
                (bom_line_id.date_start >
                 time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)) or \
                bom_line_id.date_stop and \
                (bom_line_id.date_stop <
                 time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)):
                    continue
            # all bom_line_id variant values must be in the product
            if bom_line_id.attribute_value_ids:
                if not product or \
                        (set(map(int, bom_line_id.attribute_value_ids or [])) -
                         set(map(int, product.attribute_value_ids))):
                    continue

            if previous_products and (bom_line_id.product_id.product_tmpl_id.id
                                      in previous_products):
                raise exceptions.Warning(
                    _('Invalid Action! BoM "%s" contains a BoM line with a'
                      ' product recursion: "%s".') %
                    (master_bom.name, bom_line_id.product_id.name_get()[0][1]))

            quantity = _factor(bom_line_id.product_qty * factor,
                               bom_line_id.product_efficiency,
                               bom_line_id.product_rounding)
            if not bom_line_id.product_id:
                bom_id = self._bom_find(
                    product_tmpl_id=bom_line_id.product_template.id,
                    properties=properties)
            else:
                bom_id = self._bom_find(product_id=bom_line_id.product_id.id,
                                        properties=properties)

            #  If BoM should not behave like PhantoM, just add the product,
            #  otherwise explode further
            if (bom_line_id.type != "phantom" and
                    (not bom_id or self.browse(bom_id).type != "phantom")):
                result.append({
                    'name': (bom_line_id.product_id.name or
                             bom_line_id.product_template.name),
                    'product_id': bom_line_id.product_id.id,
                    'product_template': bom_line_id.product_template.id,
                    'product_qty': quantity,
                    'product_uom': bom_line_id.product_uom.id,
                    'product_uos_qty': (bom_line_id.product_uos and
                                        _factor((bom_line_id.product_uos_qty *
                                                 factor),
                                                bom_line_id.product_efficiency,
                                                bom_line_id.product_rounding)
                                        or False),
                    'product_uos': (bom_line_id.product_uos and
                                    bom_line_id.product_uos.id or False),
                })
            elif bom_id:
                all_prod = [bom.product_tmpl_id.id] + (previous_products or [])
                bom2 = self.browse(bom_id)
                # We need to convert to units/UoM of chosen BoM
                factor2 = uom_obj._compute_qty(
                    bom_line_id.product_uom.id, quantity, bom2.product_uom.id)
                quantity2 = factor2 / bom2.product_qty
                res = self._bom_explode(
                    bom2, bom_line_id.product_id, quantity2,
                    properties=properties, level=level + 10,
                    previous_products=all_prod, master_bom=master_bom)
                result = result + res[0]
                result2 = result2 + res[1]
            else:
                raise exceptions.Warning(
                    _('Invalid Action! BoM "%s" contains a phantom BoM line'
                      ' but the product "%s" does not have any BoM defined.') %
                    (master_bom.name, bom_line_id.product_id.name_get()[0][1]))

        return result, result2


class MrpProductionAttribute(models.Model):
    _name = 'mrp.production.attribute'

    mrp_production = fields.Many2one(comodel_name='mrp.production',
                                     string='Manufacturing Order')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            #  domain="[('attribute_id','=',attribute),"
                            #  "('id','in',possible_values[0][2])]",
                            string='Value')
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')

    @api.one
    @api.depends('mrp_production.product_template')
    def _get_possible_attribute_values(self):
        domain = []
        for attr_line in (
                self.mrp_production.product_template.attribute_line_ids):
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
        if self.product_template:
            self.product_uom = self.product_template.uom_id
            product_attributes = []
            if not self.product_template.attribute_line_ids:
                self.product_id = (
                    self.product_template.product_variant_ids and
                    self.product_template.product_variant_ids[0])
            for attribute in self.product_template.attribute_line_ids:
                product_attributes.append({'attribute':
                                           attribute.attribute_id})
            self.product_attributes = product_attributes
            self.bom_id = self.env['mrp.bom']._bom_find(
                product_tmpl_id=self.product_template.id)
            self.routing_id = self.bom_id.routing_id
            return {'domain': {'product_id':
                               [('product_tmpl_id', '=',
                                 self.product_template.id)],
                               'bom_id':
                               [('product_tmpl_id', '=',
                                 self.product_template.id)]}}
        return {'domain': {}}

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        att_values_ids = [attr_line.value and attr_line.value.id
                          or False
                          for attr_line in self.product_attributes]
        domain = [('product_tmpl_id', '=', self.product_template.id)]
        for value in att_values_ids:
            domain.append(('attribute_value_ids', '=', value))
        self.product_id = product_obj.search(domain, limit=1)


class MrpProductionProductLineAttribute(models.Model):
    _name = 'mrp.production.product.line.attribute'

    product_line = fields.Many2one(
        comodel_name='mrp.production.product.line.attribute',
        string='Product line')
    attribute = fields.Many2one(comodel_name='product.attribute',
                                string='Attribute')
    value = fields.Many2one(comodel_name='product.attribute.value',
                            domain="[('attribute_id', '=', attribute)]",
                            string='Value')


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    product_id = fields.Many2one(required=False)
    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product')
    product_attributes = fields.One2many(
        comodel_name='mrp.production.product.line.attribute',
        inverse_name='product_line', string='Product attributes',
        copyable=True)

    @api.one
    @api.onchange('product_template')
    def onchange_product_template(self):
        if self.product_template:
            self.product_uom = self.product_template.uom_id
            product_attributes = []
            if not self.product_template.attribute_line_ids:
                self.product_id = (
                    self.product_template.product_variant_ids and
                    self.product_template.product_variant_ids[0])
            for attribute in self.product_template.attribute_line_ids:
                product_attributes.append({'attribute':
                                           attribute.attribute_id})
            self.product_attributes = product_attributes

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        att_values_ids = [attr_line.value and attr_line.value.id
                          or False
                          for attr_line in self.product_attributes]
        domain = [('product_tmpl_id', '=', self.product_template.id)]
        for value in att_values_ids:
            domain.append(('attribute_value_ids', '=', value))
        self.product_id = product_obj.search(domain, limit=1)
