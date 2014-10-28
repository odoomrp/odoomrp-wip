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

from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_open_quants(self):
        template_obj = self.env['product.template']
        products = self.env['product.product']
        for line in self.order_line:
            products |= line.product_id
        result = template_obj._get_act_window_dict('stock.product_open_quants')
        result['domain'] = "[('product_id', 'in', " + str(products.ids) + ")]"
        result['context'] = {'search_default_productgroup': 1,
                             'search_default_internal_loc': 1}
        return result
