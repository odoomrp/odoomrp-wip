
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


class MrpBom(models.Model):
    
    _inherit = "mrp.bom"
    
    def get_product_components(self, product_id=None, accumulated_qty=None):
        all_components = []
        bom_id = self._bom_find(product_id=product_id,
                                   properties=[])
        if not bom_id:
            return False
        bom = self.browse(bom_id)
        if not bom.bom_line_ids or not bom.type=='normal':
            return False
        for line in bom.bom_line_ids:
            qty=line.product_qty/bom.product_qty*accumulated_qty
            components = self.get_product_components(
                product_id=line.product_id.id, accumulated_qty=qty)
            if not components:
                all_components.append([line.product_id.id, qty])
            else:
                all_components.extend(components)
        return all_components


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

    def get_new_components_info(self, product_id, loc_id, loc_dest_id,
                                uom_id, uos_id, qty):
        move_obj=self.env['stock.move']
        ul_move = move_obj.onchange_product_id(
            prod_id=product_id,
            loc_id=loc_id,
            loc_dest_id=loc_dest_id)
        ul_move['value'].update({
            'product_id': product_id,
            'product_uom': uom_id,
            'product_uos': uos_id,
            'product_qty': qty,
            'product_uos_qty': move_obj.onchange_quantity(
                product_id, qty, uom_id,
                uos_id)['value']['product_uos_qty']})
        return ul_move['value']

    @api.one
    def create_mo_from_download_operation(self):
        move_obj = self.env['stock.move']
        bom_obj = self.env['mrp.bom']
        prod_obj = self.env['product.product']
        res=[]
        for op in self.pack:
            conts = bom_obj.get_product_components(
                product_id=op.ul.product.id, accumulated_qty=op.ul.ul_qty)
            if not conts:
                value = self.get_new_components_info(
                    op.ul.product.id,
                    op.ul.product.property_stock_production.id,
                    op.ul.product.property_stock_inventory.id,
                    op.ul.product.uom_id.id, op.ul.product.uos_id.id, qty)
                res.append(value)

            else:
                for cont in conts:
                    product = prod_obj.browse(cont[0])
                    qty = cont[1]
                    value = self.get_new_components_info(
                        product.id, product.property_stock_production.id,
                        product.property_stock_inventory.id, product.uom_id.id,
                        product.uos_id.id, qty)
                    res.append(value)
            bulk_value = self.get_new_components_info(
                self.product_id.id,
                self.location_src_id.id,
                self.location_dest_id.id,
                self.product_id.uom_id.id, self.product_id.uos_id.id, op.fill)
            res.append(bulk_value)
            data = self.product_id_change(op.product.id, op.qty)
            data['value'].update({
                'product_id': op.product.id,
                'location_id': op.product.property_stock_production.id,
                'loc_dest_id': op.product.property_stock_inventory.id,
                'product_qty': op.qty,
                'product_lines': map(lambda x: (0, 0, x), res),
                                })
            new_op = self.create(data['value'])
            self.action_compute()
