
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class WizProductionProductLine(models.TransientModel):
    _name = 'wiz.production.product.line'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Product Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    production_id = fields.Many2one(
        'mrp.production', 'Production Order', select=True,
        default=lambda self: self.env.context.get('production_id', False))
    work_order = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order')

    @api.multi
    def add_product(self):
        production_obj = self.env['mrp.production']
        st_move_obj = self.env['stock.move']
        mppl_obj = self.env['mrp.production.product.line']
        values = {'product_id': self.product_id.id,
                  'product_qty': self.product_qty,
                  'production_id': self.production_id.id,
                  'work_order': self.work_order.id,
                  'name': self.product_id.name}
        result = production_obj.product_id_change(
            product_id=self.product_id.id,
            product_qty=self.product_qty, context=self.env.context)
        values.update(result['value'])
        line = mppl_obj.create(values)
        consume_id = production_obj._make_production_consume_line(line)
        consume = st_move_obj.browse(consume_id)
        consume.work_order = self.work_order.id
        return True
