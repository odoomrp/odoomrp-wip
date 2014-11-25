
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

from openerp import api, models


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

    @api.one
    def action_compute(self):
        res = []
        result = super(MrpProduction, self).action_compute()
        workorder =\
            self.workcenter_lines and self.workcenter_lines[0].id
        for attr_value in self.product_id.attribute_value_ids:
            if (attr_value.linked_product and
                    attr_value.linked_product.id not in
                    self.product_lines.ids):
                value = self.get_new_components_info(
                    attr_value.linked_product.id,
                    attr_value.linked_product.property_stock_production.id,
                    attr_value.linked_product.property_stock_inventory.id,
                    attr_value.linked_product.uom_id.id,
                    attr_value.linked_product.uos_id.id,
                    self.product_qty, workorder)
            res.append(value)
        self.write({'product_lines': map(lambda x: (0, 0, x), res)})
        return result
