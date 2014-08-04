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
import openerp.addons.decimal_precision as dp


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

    def _calc_price_subtotal(self, cr, uid, line, context=None):
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        extra_discount = line.discount2 or 0.0
        return price * (1 - extra_discount / 100.0)
    
    def _calc_qty(self, cr, uid, line, context=None):
        qty = line.product_qty
        if line.offer_id:
            total = line.offer_id.free_qty + line.offer_id.paid_qty
            qty = round((qty / total) * line.offer_id.paid_qty)
        return qty

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool['res.currency']
        tax_obj = self.pool['account.tax']
        for line in self.browse(cr, uid, ids):
            new_price_subtotal = self._calc_price_subtotal(cr, uid, line)
            qty = self._calc_qty(cr, uid, line)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id,
                                        new_price_subtotal, qty,
                                        line.product_id,
                                        line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        # 'discount': fields.float('Discount (%)',
                                  # digits_compute=dp.get_precision('Discount')),
                                  # readonly=True,
                                  # states={'draft': [('readonly', False)]}),
        'discount2': fields.float('Discount (%)',
                                  digits_compute=dp.get_precision('Discount')),
                                  # readonly=True,
                                  # states={'draft': [('readonly', False)]}),
        'offer_id': fields.many2one('product.pricelist.item.offer', 'Offer'),
        'item_id': fields.many2one('product.pricelist.item', 'Pricelist Item'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal',
                                          digits_compute=
                                          dp.get_precision('Account')),
        'subtotal_ids': fields.one2many('purchase.order.line.subtotal',
                                        'line_id',
                                        'Subtotals by pricelist'),
    }

    _defaults = {
        # 'discount': 0.0,
        'discount2': 0.0,
    }

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Second discount must be lower than 100%.'),
    ]

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(PurchaseOrderLine, self).default_get(cr, uid, fields_list,
                                                         context=context)
        item_obj = self.pool['product.pricelist.item']
        if context.get('pricelist_id'):
            item_id = item_obj.get_best_pricelist_item(cr, uid,
                                                       context['pricelist_id'],
                                                       context=context)
            res.update({'item_id': item_id})
        return res

    def onchange_item_id(self, cr, uid, ids, item_id, context=None):
        if not item_id:
            return {}
        item_obj = self.pool['product.pricelist.item']
        item = item_obj.browse(cr, uid, item_id, context=context)
        values = {
            'discount': item.discount,
            'discount2': item.discount2,
            'offer_id': item.offer_id.id,
        }
        return {'value': values}

class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        tax_obj = self.pool['account.tax']
        line_obj = self.pool['purchase.order.line']
        new_price_subtotal = line_obj._calc_price_subtotal(cr, uid, line)
        qty = line_obj._calc_qty(cr, uid, line)
        for c in tax_obj.compute_all(cr, uid, line.tax_id, new_price_subtotal,
                                     qty, line.product_id,
                                     line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    _columns = {
        'subtotal_ids': fields.one2many('purchase.order.line.subtotal',
                                        'purchase_id',
                                        'Subtotals per line by pricelist')
    }
