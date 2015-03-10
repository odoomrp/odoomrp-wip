# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.one
    @api.depends('bom_line_ids', 'bom_line_ids.product_qty')
    def _compute_qtytoconsume(self):
        self.qty_to_consume = sum(x.product_qty for x in self.bom_line_ids)

    by_percentage = fields.Boolean(string='Produce by percentage')
    qty_to_consume = fields.Float(
        string='QTY to consume', compute='_compute_qtytoconsume',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.one
    @api.onchange('by_percentage', 'bom_line_ids')
    def onchange_by_percentage(self):
        self.qty_to_consume = sum(x.product_qty for x in self.bom_line_ids)
        if self.by_percentage:
            self.product_qty = 100

    @api.one
    @api.constrains('by_percentage', 'qty_to_consume', 'bom_line_ids')
    def _check_by_percentage(self):
        if self.by_percentage and self.qty_to_consume != 100:
            raise exceptions.Warning(_('Quantity to consume <> 100'))
