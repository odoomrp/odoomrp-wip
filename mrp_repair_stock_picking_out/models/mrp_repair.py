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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    stock_picking = fields.Many2one('stock.picking', string='Picking')

    @api.multi
    def action_repair_done(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        res = super(MrpRepair, self).action_repair_done()
        if self.address_id and self.move_id:
            StockPicking = self.env['stock.picking']
            StockPickingType = self.env['stock.picking.type']
            outgoing_type = StockPickingType.search(
                [('code', '=', 'outgoing')])
            values = {
                'origin': self.move_id.origin,
                'company_id': self.move_id.company_id and
                self.move_id.company_id.id or False,
                'move_type': self.move_id.group_id and
                self.move_id.group_id.move_type or 'direct',
                'partner_id': self.move_id.partner_id.id or False,
                'picking_type_id': outgoing_type.id
            }
            pick = StockPicking.create(values)
            self.stock_picking = pick
            self.move_id.write({'picking_type_id': outgoing_type.id,
                                'picking_id': pick.id})
        return res
