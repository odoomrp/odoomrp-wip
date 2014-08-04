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
import time


class PricelistOffer(orm.Model):
    _name = 'product.pricelist.item.offer'

    _columns = {
        'name': fields.char('Offer Name', size=16),
        'paid_qty': fields.integer('Paid quantity'),
        'free_qty': fields.integer('Free quantity'),
    }


class PricelistItem(orm.Model):
    _inherit = 'product.pricelist.item'

    _columns = {
        'offer_id': fields.many2one('product.pricelist.item.offer', 'Offer'),
        'discount': fields.float('Discount %',
                                 digits_compute=dp.get_precision(
                                     'Product Price')),
        'discount2': fields.float('Discount 2 %',
                                  digits_compute=dp.get_precision(
                                      'Product Price')),
    }

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Second discount must be lower than 100%.'),
    ]

    def domain_by_pricelist(self, cr, uid, pricelist_id, context=None):
        vers_obj = self.pool['product.pricelist.version']
        today = time.strftime('%Y-%m-%d')
        vers_ids = vers_obj.search(cr, uid,
                                   [('pricelist_id', '=', pricelist_id),
                                    '|', ('date_start', '=', False),
                                    ('date_start', '<=', today),
                                    '|', ('date_end', '=', False),
                                    ('date_end', '>=', today)],
                                   context=context)
        item_ids = self.search(cr, uid, [('price_version_id', 'in', vers_ids)],
                               order='sequence', context=context)
        for item in self.browse(cr, uid, item_ids, context=context):
            if item.base == -1:
                item_ids.remove(item.id)
                new_item_ids = self.domain_by_pricelist(
                    cr, uid, item.base_pricelist_id.id, context=context)
                item_ids += new_item_ids
        return item_ids

    def get_best_pricelist_item(self, cr, uid, pricelist_id, context=None):
        pricelist_item_id = False
        pricelist_item_ids = self.domain_by_pricelist(
            cr, uid, pricelist_id, context=context)
        if pricelist_item_ids:
            pricelist_item_id = pricelist_item_ids[0]
        return pricelist_item_id
