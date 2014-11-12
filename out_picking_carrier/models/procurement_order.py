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

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def run(self, autocommit=False):
        sale_obj = self.env['sale.order']
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        for rec in self:
            for move in rec.move_ids:
                if (move.origin and move.picking_id.picking_type_id and
                        move.picking_id.picking_type_id.code == 'outgoing'):
                    order = sale_obj.search([('name', '=', move.origin)],
                                            limit=1)
                    if order:
                        if order.carrier_id and not move.picking_id.carrier_id:
                            move.picking_id.carrier_id = order.carrier_id.id
        return res
