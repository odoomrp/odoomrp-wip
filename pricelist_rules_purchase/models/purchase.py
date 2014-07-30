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

from openerp.osv import orm, fields


class PurchaseOrderLineSubtotal(orm.Model):
    _name = 'purchase.order.line.subtotal'

    def _calculate_subtotal(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool['res.currency']
        tax_obj = self.pool['account.tax']

        for item in self.browse(cr, uid, ids, context=context):
            price = (item.line_id.price_unit * 
                     (1 - (item.item_id.discount or 0.0) / 100) *
                     (1 - (item.item_id.discount2 or 0.0) / 100))

            qty = item.line_id.product_uom_qty
            if item.item_id.offer_id:
                total = (item.item_id.offer_id.free_qty +
                         item.item_id.offer_id.paid_qty)
                qty = round((qty / total) * item.item_id.offer_id.paid_qty)

            taxes = tax_obj.compute_all(cr, uid, item.line_id.tax_id,
                                        price, qty,
                                        item.line_id.product_id,
                                        item.order_id.partner_id)
            cur = item.order_id.pricelist_id.currency_id
            res[item.id] = cur_obj.round(cr, uid, cur, taxes['total'])

        return res

    _columns = {
        'line_id': fields.many2one('purchase.order.line', 'Line',
                                   ondelete='cascade'),
        'purchase_id': fields.related('line_id', 'order_id', type='many2one',
                                  relation='purchase.order',
                                  string='Purchase Order', store=True),
        'item_id': fields.many2one('product.pricelist.item', 'Pricelist Item',
                                   ondelete='cascade'),
        'subtotal': fields.function(_calculate_subtotal, type='float',
                                    method=True, string='Subtotal',
                                    obj='purchase.order.pricelist.version'),
    }


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

