# -*- coding: utf-8 -*-
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

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class WizProductionProductLine(models.TransientModel):
    _name = 'wiz.production.product.line'

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    product_qty = fields.Float(
        string='Product Quantity', required=True,
        digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='Unit of Measure')
    production_id = fields.Many2one(
        comodel_name='mrp.production', string='Production Order', select=True,
        default=lambda self: self.env.context.get('active_id', False))

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id
        self.product_qty = 1.0 if not self.product_qty and self.product_id \
            else self.product_qty

    @api.constrains('product_uom_id')
    def _check_product_uom_id(self):
        for record in self:
            if record.product_id.uom_id.category_id != \
                    record.product_uom_id.category_id:
                raise exceptions.ValidationError(
                    _('Please use an UoM in the same UoM category.'))

    def _prepare_product_addition(
            self, product, product_qty, product_uom, production):
        addition_vals = {
            'product_id': product.id,
            'product_uom': product_uom.id or product.uom_id.id,
            'product_qty': product_qty,
            'production_id': production.id,
            'name': product.name,
            'addition': True
        }
        return addition_vals

    @api.multi
    def add_product(self):
        move_obj = self.env['stock.move']
        if self.product_qty <= 0:
            raise exceptions.Warning(
                _('Warning'), _('Please provide a positive quantity to add'))
        mppl_obj = self.env['mrp.production.product.line']
        production_obj = self.env['mrp.production']
        values = self._prepare_product_addition(
            self.product_id, self.product_qty, self.product_uom_id,
            self.production_id)
        line = mppl_obj.create(values)
        move_id = production_obj._make_production_consume_line(line)
        move = move_obj.browse(move_id)
        move.action_confirm()
        if self.production_id.state not in 'confirmed':
            move.action_assign()
        return move
