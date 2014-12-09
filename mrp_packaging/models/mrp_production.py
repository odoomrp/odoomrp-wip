
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

from openerp import api, fields, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    pack = fields.One2many('packaging.operation', 'operation')
    expected_production = fields.One2many('mrp.production', 'production',
                                          string='Expected Production',
                                          )
    production = fields.Many2one('mrp.production', string='Production')

    @api.one
    def get_dump_packages(self):
        pack_lines = []
        lines = self.env['mrp.bom.line'].search(
            ['|', ('product_template', '=', self.product_template.id),
             ('product_id', '=', self.product_id.id)])
        for line in lines:
            pack_line = map(
                lambda x: (0, 0, {'product': x}),
                line.bom_id.product_tmpl_id.product_variant_ids.ids)
            pack_lines.extend(pack_line)
        self.write({'pack': pack_lines})

    @api.one
    def create_mo_from_packaging_operation(self):
        for op in self.pack:
            res = []
            add_product = []
            if op.processed or op.qty == 0:
                continue
            final_product_qty = op.fill if op.product.uom_id.id ==\
                self.product_id.uom_id.id else op.qty
            data = self.product_id_change(op.product.id, final_product_qty)
            product_attributes = map(
                lambda x: (0, 0, x),
                data['value']['product_attributes'])
            data['value'].update({
                'product_id': op.product.id,
                'product_qty': final_product_qty,
                'product_attributes': product_attributes})
            new_op = self.create(data['value'])
            new_op.action_compute()
            workorder =\
                new_op.workcenter_lines and new_op.workcenter_lines[0].id
            for attr_value in op.product.attribute_value_ids:
                raw_product = attr_value.raw_product
                if raw_product:
                    value = self.get_new_components_info(
                        raw_product.id,
                        raw_product.property_stock_production.id,
                        raw_product.property_stock_inventory.id,
                        raw_product.uom_id.id,
                        raw_product.uos_id.id,
                        op.qty, workorder)
                    res.append(value)
            for line in new_op.product_lines:
                if self.product_id.product_tmpl_id == line.product_template:
                    new_op.write({'product_lines':
                                  [(1, line.id,
                                    {'product_id': self.product_id.id})]})
                    continue
                for link_product in res:
                    if link_product['product_id'] == line.product_id.id:
                        new_op.write({'product_lines': [(1, line.id,
                                                         link_product)]})
                    else:
                        add_product.append(link_product)
            new_op.write({'product_lines': map(lambda x: (0, 0, x),
                                               add_product),
                          'production': self.id,
                          'origin': self.name})
            op.processed = True


class PackagingOperation(models.Model):
    _name = "packaging.operation"
    _rec_name = 'product'

    @api.one
    def _calculate_weight(self):
        raw_qty = 1
        for value in self.product.attribute_value_ids:
            if value.raw_product:
                raw_qty = value.numeric_value
                break
        self.fill = raw_qty * self.qty

    product = fields.Many2one('product.product', string='Product',
                              required=True,
                              help="Product that is going to be manufactured")
    operation = fields.Many2one('mrp.production')
    qty = fields.Integer(string="QTY",
                         help="Product Quantity. It will be the new "
                         "manufacturing order quantity "
                         "if dump uom is equal to product uom")
    fill = fields.Float(string="Fill", compute=_calculate_weight,
                        help="Product linked raw material value *"
                        "Product Quantity. It will be the new manufacturing "
                        "order quantity "
                        "if dump uom is not equal to product uom")
    processed = fields.Boolean(string='Processed')
