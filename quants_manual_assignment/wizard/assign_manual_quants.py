
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

from openerp import fields, models, api


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'
    _rec_name = 'quants_lines'

    quants_lines = fields.One2many('assign.manual.quants.lines', 'move',
                                   string='Quants')

    @api.multi
    def assign_quants(self):
        move = self.env['stock.move'].browse(self.env.context['active_ids'][0])
        quants = []
        for line in self.quants_lines:
            if line.selected:
                quants.append(line.quant.id)
        move.write({'reserved_quant_ids':
                    [(6, 0, quants)]})
        return {}

    def default_get(self, cr, uid, fiels, context=None):
        unassign_lines = []
        move = self.pool['stock.move'].browse(
            cr, uid, context['active_ids'][0], context=context)
        available_quants_ids = self.pool['stock.quant'].search(
            cr, uid, [
                '|', ('location_id', '=', move.location_id.id),
                ('location_id', 'in', move.location_id.child_ids.ids),
                ('product_id', '=', move.product_id.id),
                ('qty', '>', 0),
                ('reservation_id', '=', False)], context=context)
        available_quants = [{'quant': x} for x in available_quants_ids]
        available_quants.extend(
            {'quant': x,
             'selected': True
             } for x in move.reserved_quant_ids.ids)
        return {'quants_lines': available_quants}


class AssignManualQuantsLines(models.TransientModel):
    _name = 'assign.manual.quants.lines'
    _rec_name = 'quant'

    move = fields.Many2one('assign.manual.quants', string='Move')
    quant = fields.Many2one('stock.quant', string="Quant")
    selected = fields.Boolean(string="Select")
