
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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_sale_product_prices(self):
        data_obj = self.env['ir.model.data']
        sale_line_obj = self.env['sale.order.line']
        id2 = data_obj._get_id('product_last_prices',
                               'last_sale_product_prices_view')
        if id2:
            id2 = data_obj.browse(id2).res_id
        sale_line_lst = []
        for order_line in self.order_line:
            sale_line = sale_line_obj.search(
                [('order_id', '!=', self.id),
                 ('product_id', '=', order_line.product_id.id)],
                order='create_date DESC', limit=1)
            sale_line_lst.append(sale_line.id)
        return {
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'sale.order.line',
            'views': [(id2, 'tree')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': "[('id','in',["+','.join(map(str, sale_line_lst))+"])]",
            }
