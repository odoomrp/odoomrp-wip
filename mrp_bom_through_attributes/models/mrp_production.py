
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

from openerp import api, models, fields


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def get_new_components_info(self, product_id, loc_id, loc_dest_id,
                                uom_id, uos_id, qty, workorder):
        move_obj = self.env['stock.move']
        ul_move = move_obj.onchange_product_id(
            prod_id=product_id,
            loc_id=loc_id,
            loc_dest_id=loc_dest_id)
        ul_move['value'].update({
            'product_id': product_id,
            'product_uom': uom_id,
            'product_uos': uos_id,
            'product_qty': qty,
            'work_order': workorder,
            'product_uos_qty': move_obj.onchange_quantity(
                product_id, qty, uom_id,
                uos_id)['value']['product_uos_qty']})
        return ul_move['value']

    def get_raw_products_data(self):
        res = []
        workorder =\
            self.workcenter_lines and self.workcenter_lines[0].id
        for attr_value in self.product_id.attribute_value_ids:
            raw_product = attr_value.raw_product
            value = self.get_new_components_info(
                raw_product.id,
                raw_product.property_stock_production.id,
                raw_product.property_stock_inventory.id,
                raw_product.uom_id.id,
                raw_product.uos_id.id,
                self.product_qty * attr_value.raw_qty,
                workorder)
            res.append(value)
        return res

    @api.one
    def action_compute(self):
        result = super(MrpProduction, self).action_compute()
        res = self.get_raw_products_data()
        self.write({'product_lines': map(lambda x: (0, 0, x), res)})
        return result

    product_id = fields.Many2one()

    @api.one
    @api.onchange('product_id')
    def onchange_bring_raw_products(self):
        res = self.get_raw_products_data()
        self.raw_products = res

    raw_products = fields.One2many('mrp.production.product.line',
                                   'raw_production', string='Raw Products')


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'
    raw_production = fields.Many2one('mrp.production', string='Production')
