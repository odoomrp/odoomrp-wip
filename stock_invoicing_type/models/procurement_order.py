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
            for stock_move in rec.move_ids:
                if stock_move.picking_id and \
                        not stock_move.picking_id.invoice_type_id:
                    orders = sale_obj.search([('procurement_group_id', '=',
                                               stock_move.group_id.id)])
                    if orders:
                        invoice_type = orders[0].invoice_type_id.id
                        picking = stock_move.picking_id
                        picking.invoice_type_id = invoice_type
        return res
