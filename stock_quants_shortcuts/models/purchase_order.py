
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    def _get_products(self):
        products = []
        for purchase in self:
            products += [x.product_id.id for x in purchase.order_line]
        return products

    @api.multi
    def action_open_quants(self):
        template_obj = self.env['product.template']
        products = self._get_products()
        result = template_obj._get_act_window_dict('stock.product_open_quants')
        result['domain'] = "[('product_id','in',[" + ','.join(
            map(str, products)) + "])]"
        result['context'] = ("{'search_default_productgroup': 1, "
                             "'search_default_internal_loc': 1}")
        return result
