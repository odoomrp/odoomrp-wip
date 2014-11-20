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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import time


class PricelistOffer(models.Model):
    _name = 'product.pricelist.item.offer'

    name = fields.Char(string='Offer Name')
    paid_qty = fields.Integer(string='Paid quantity')
    free_qty = fields.Integer(string='Free quantity')


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    pricelist = fields.Many2one(comodel_name='product.pricelist',
                                related='price_version_id.pricelist_id',
                                string='Pricelist', store=True)
    pricelist_type = fields.Selection(
        string='Pricelist Type', related='pricelist.type', store=True)
    offer = fields.Many2one(
        comodel_name='product.pricelist.item.offer', string='Offer')
    discount = fields.Float('Discount %',
                            digits=dp.get_precision('Product Price'))
    discount2 = fields.Float('Discount 2 %',
                             digits=dp.get_precision('Product Price'))
    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')
    item_formula = fields.Char(compute='_item_formula')

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Second discount must be lower than 100%.'),
    ]

    @api.one
    def _item_formula(self):
        self.item_formula = (_('Base price * (1 + %s) + %s') %
                             (self.price_discount, self.price_discount))

    @api.model
    def domain_by_pricelist(self, pricelist_id):
        vers_obj = self.env['product.pricelist.version']
        today = time.strftime('%Y-%m-%d')
        vers_ids = vers_obj.search([('pricelist_id', '=', pricelist_id),
                                    '|', ('date_start', '=', False),
                                    ('date_start', '<=', today),
                                    '|', ('date_end', '=', False),
                                    ('date_end', '>=', today)])
        item_ids = self.search([('price_version_id', 'in', vers_ids.ids)],
                               order='sequence')
        for item in item_ids:
            if item.base == -1:
                item_ids.remove(item)
                new_item_ids = self.domain_by_pricelist(
                    item.base_pricelist_id)
                item_ids += new_item_ids
        return item_ids.ids

    @api.model
    def get_best_pricelist_item(self, pricelist_id):
        pricelist_item_id = False
        pricelist_item_ids = self.domain_by_pricelist(pricelist_id)
        if pricelist_item_ids:
            pricelist_item_id = pricelist_item_ids[0]
        return pricelist_item_id
