
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

from openerp import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_data = fields.Datetime(
        comodel_name='sale.order', string='Sale Date',
        related='order_id.date_order', store=True)

    @api.multi
    def action_sale_product_prices(self):
        id2 = self.env.ref(
            'sale_order_last_prices.last_sale_product_prices_view')
        sale_lines = self.search(
            [('order_id', '!=', self.id),
             ('product_id', '=', self.product_id.id)],
            order='create_date DESC')
        return {
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'sale.order.line',
            'views': [(id2.id, 'tree')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': "[('id','in',["+','.join(map(str, sale_lines.ids))+"])]",
            }
