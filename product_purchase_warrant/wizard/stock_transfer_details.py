
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

from openerp import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime


class StockTransferDetails(models.TransientModel):

    _inherit = "stock.transfer_details"

    def get_warrant(self, cr, uid, result, context=None):
        sup_obj = self.pool['product.supplierinfo']
        prod_obj = self.pool['product.product']
        for pick in self.pool['stock.picking'].browse(
                cr, uid, context['active_ids'], context=context):
            if pick.location_id.usage == 'supplier':
                for item in result['item_ids'] + result['packop_ids']:
                    product = prod_obj.browse(cr, uid, item['product_id'],
                                              context=context)[0]
                    sup = sup_obj.search(
                        cr, uid, [('name', '=', pick.partner_id.id),
                                  ('product_tmpl_id', '=',
                                   product.product_tmpl_id.id)],
                        context=context)
                    warrant = sup and sup_obj.browse(
                        cr, uid, sup[0],
                        context=context).warrant_months or product.warranty
                    item.update({'warrant': datetime.now() +
                                 relativedelta(months=int(warrant)) +
                                 relativedelta(
                        days=int(31*(warrant - int(warrant))))})
        return result

    def default_get(self, cr, uid, fields, context=None):
        res = super(StockTransferDetails, self).default_get(cr, uid, fields,
                                                            context=context)
        result = res.copy()
        return self.get_warrant(cr, uid, result, context=context)


class TransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    warrant = fields.Datetime(string='Warrant')
