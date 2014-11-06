
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def action_purchase_product_prices(self):
        id2 = self.env.ref(
            'purchase_order_last_prices.last_purchase_product_prices_view')
        purchase_lines = self.search(
            [('order_id', '!=', self.order_id.id),
             ('product_id', '=', self.product_id.id)],
            order='create_date DESC')
        return {
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'purchase.order.line',
            'views': [(id2.id, 'tree')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': "[('id','in',["+','.join(map(str,
                                                   purchase_lines.ids))+"])]",
            }
