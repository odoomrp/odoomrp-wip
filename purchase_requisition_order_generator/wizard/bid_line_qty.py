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

from openerp import models, api


class BidLineQty(models.TransientModel):
    _inherit = "bid.line.qty"

    @api.one
    def change_qty(self):
        purchase_line_obj = self.env['purchase.order.line']
        active_ids = self._context and self._context.get('active_ids', [])
        for line in purchase_line_obj.browse(active_ids):
            line.update({'product_qty': self.qty})
        return {'type': 'ir.actions.act_window_close'}
