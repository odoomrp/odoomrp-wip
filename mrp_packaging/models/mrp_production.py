
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

    pack = fields.One2many('download.operation', 'operation')
    claim = fields.Many2one('crm.claim')
    download_user = fields.Many2one('res.users')
    sample = fields.Many2many('mrp.sample')
    sample_taken = fields.Boolean('Samples Taken')
    expected_production = fields.One2many('mrp.production', 'production',
                                          string='Expected Production',
                                          )
    production = fields.Many2one('mrp.production', string='Production')

    @api.one
    def get_dump_packages(self):
        pack_lines = []
        lines = self.env['mrp.bom.line'].search([('product_id', '=',
                                                  self.product_id.id)])
        for line in lines:
            pack_line = map(
                lambda x: (0, 0, {'product': x}),
                line.bom_id.product_tmpl_id.product_variant_ids.ids)
            pack_lines.extend(pack_line)
        self.write({'pack': pack_lines})

    @api.one
    def create_mo_from_download_operation(self):
        for op in self.pack:
            res = []
            add_product = []
            if op.processed or op.qty == 0:
                continue
            final_product_qty = op.fill if op.product.uom_id.id ==\
                self.product_id.uom_id.id else op.qty
            data = self.product_id_change(op.product.id, final_product_qty)
            data['value'].update({
                'product_id': op.product.id,
                'location_id': op.product.property_stock_production.id,
                'loc_dest_id': op.product.property_stock_inventory.id,
                'product_qty': final_product_qty})
            new_op = self.create(data['value'])
            new_op.action_compute()
            workorder =\
                new_op.workcenter_lines and new_op.workcenter_lines[0].id
            for attr_value in op.product.attribute_value_ids:
                if attr_value.linked_product:
                    value = self.get_new_components_info(
                        attr_value.linked_product.id,
                        attr_value.linked_product.property_stock_production.id,
                        attr_value.linked_product.property_stock_inventory.id,
                        attr_value.linked_product.uom_id.id,
                        attr_value.linked_product.uos_id.id,
                        op.qty, workorder)
                res.append(value)
            bulk_value = self.get_new_components_info(
                self.product_id.id,
                self.location_src_id.id,
                self.location_dest_id.id,
                self.product_id.uom_id.id, self.product_id.uos_id.id, op.fill,
                workorder)
            for line in new_op.product_lines:
                if bulk_value['product_id'] == line.product_id.id:
                    new_op.write({'product_lines': [(1, line.id, bulk_value)]})
                    continue
                for link_product in res:
                    if link_product['product_id'] == line.product_id.id:
                        new_op.write({'product_lines': [(1, line.id,
                                                         link_product)]})
                        break
                    add_product.append(link_product)
            new_op.write({'product_lines': map(lambda x: (0, 0, x),
                                               add_product),
                          'production': self.id,
                          'origin': self.name})
            op.processed = True


class DownloadOperation(models.Model):
    _name = "download.operation"
    _rec_name = 'product'

    @api.one
    def _calculate_weight(self):
        numeric_value = 1
        for value in self.product.attribute_value_ids:
            if value.linked_product:
                numeric_value = value.numeric_value
                break
        self.fill = numeric_value * self.qty

    product = fields.Many2one('product.product', string='Product',
                              required=True)
    operation = fields.Many2one('mrp.production')
    qty = fields.Integer(string="QTY")
    fill = fields.Float(string="Fill", compute=_calculate_weight)
    processed = fields.Boolean(string='Processed')


class MrpSample(models.Model):
    _name = 'mrp.sample'

    name = fields.Char(string='Name')
