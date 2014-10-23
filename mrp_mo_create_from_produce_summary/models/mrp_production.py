
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import api, fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    expected_production = fields.One2many('mrp.production', 'production',
                                          string='Expected Production',
                                          )
    production = fields.Many2one('mrp.production', string='Production')

    @api.one
    def bring_expected_production(self):
        ids = []
        for line in self.move_lines:
            for mo in self.search([('product_id', '=', line.product_id.id)]):
                if mo.state in ['draft', 'confirmed']:
                    ids.append(mo.id)
        self.expected_production = [(6, 0, ids)]

    @api.one
    def create_mo_from_download_operation(self):
        move_obj = self.env['stock.move']
        for op in self.pack:
            ul_move = move_obj.onchange_product_id(
                prod_id=op.ul.product.id,
                loc_id=op.ul.product.property_stock_production.id,
                loc_dest_id=op.ul.product.property_stock_inventory.id)
            ul_move['value'].update({
                'product_id': op.ul.product.id,
                'location_id': op.ul.product.property_stock_production.id,
                'loc_dest_id': op.ul.product.property_stock_inventory.id,
                'product_uom_qty': op.ul.ul_qty,
                'product_uos_qty': move_obj.onchange_quantity(
                    op.ul.product.id, op.ul.ul_qty, op.ul.product.uom_id.id,
                    op.ul.product.uos_id.id)['value']['product_uos_qty']})
            ul_bulk = move_obj.onchange_product_id(
                prod_id=self.product_id.id, loc_id=self.location_src_id.id,
                loc_dest_id=self.location_dest_id.id)
            ul_bulk['value'].update({
                'product_id': self.product_id.id,
                'location_id': self.product_id.property_stock_production.id,
                'loc_dest_id': self.product_id.property_stock_inventory.id,
                'product_uom_qty': op.fill,
                'product_uos_qty': move_obj.onchange_quantity(
                    self.product_id.id, op.fill, self.product_id.uom_id.id,
                    self.product_id.uos_id.id)['value']['product_uos_qty']})
            data = self.product_id_change(op.product.id, op.qty)
            data['value'].update({
                'product_id': op.product.id,
                'location_id': op.product.property_stock_production.id,
                'loc_dest_id': op.product.property_stock_inventory.id,
                'product_qty': op.qty,
                'move_lines': [(0, 0, ul_move['value']),
                               (0, 0, ul_bulk['value'])]})
            new_op = self.create(data['value'])
