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

from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp


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
    discount2 = fields.Float('Disc. 2 %',
                             digits=dp.get_precision('Product Price'))
    discount3 = fields.Float('Disc. 3 %',
                             digits=dp.get_precision('Product Price'))
    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')
    item_formula = fields.Char(compute='_item_formula')

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Second discount must be lower than 100%.'),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         _('Third discount must be lower than 100%.')),
    ]

    price_version_id = fields.Many2one()

    @api.onchange('price_version_id')
    def onchange_price_version(self):
        self.pricelist = self.price_version_id.pricelist_id

    @api.one
    def _item_formula(self):
        self.item_formula = (_('Base price * (1 + %s) + %s') %
                             (self.price_discount, self.price_surcharge))

    @api.model
    def domain_by_pricelist(self, pricelist_id, product_id=False,
                            product_tmpl_id=False, categ_id=False, qty=0,
                            partner_id=False):
        vers_obj = self.env['product.pricelist.version']
        suppinfo_obj = self.env['product.supplierinfo']
        today = fields.Date.context_today(self)
        vers_ids = vers_obj.search([('pricelist_id', '=', pricelist_id),
                                    '|', ('date_start', '=', False),
                                    ('date_start', '<=', today),
                                    '|', ('date_end', '=', False),
                                    ('date_end', '>=', today)])
        domain = [('price_version_id', 'in', vers_ids.ids),
                  '&', ('min_quantity', '<=', qty)]
        if product_id:
            product_obj = self.env['product.product']
            product = product_obj.browse(product_id)
            domain.extend([
                '|', ('product_id', '=', product_id),
                '|', '&', ('product_id', '=', False),
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                '|', '&', ('product_id', '=', False),
                '&', ('product_tmpl_id', '=', False),
                ('categ_id', '=', product.categ_id.id),
            ])
        elif product_tmpl_id:
            template_obj = self.env['product.template']
            template = template_obj.browse(product_tmpl_id)
            domain.extend([
                '|', '&', ('product_id', '=', False),
                ('product_tmpl_id', '=', template.id),
                '|', '&', ('product_id', '=', False),
                '&', ('product_tmpl_id', '=', False),
                ('categ_id', '=', template.categ_id.id),
            ])
        domain.extend(['&', ('product_id', '=', False),
                       '&', ('product_tmpl_id', '=', False),
                       ('categ_id', '=', False)])
        items = self.search(domain, order='sequence asc,min_quantity desc')
        item_ids = items.ids
        for item in items:
            if item.base == -2:
                if item.pricelist.type == 'sale':
                    suppinfo_obj = suppinfo_obj.with_context(
                        supplierinfo_type='customer')
                tmpl_id = product_tmpl_id
                if not tmpl_id and product_id:
                    tmpl_id = product_obj.browse(product_id).product_tmpl_id.id
                suppinfos = suppinfo_obj.search(
                    [('product_tmpl_id', '=', tmpl_id),
                     ('name', '=', partner_id)])
                if not suppinfos.mapped('pricelist_ids'):
                    item_ids.remove(item.id)
        return item_ids

    @api.model
    def get_best_pricelist_item(self, pricelist_id, product_id=False,
                                product_tmpl_id=False, categ_id=False, qty=0,
                                partner_id=False):
        pricelist_item_id = False
        pricelist_item_ids = self.domain_by_pricelist(
            pricelist_id, product_id=product_id,
            product_tmpl_id=product_tmpl_id, categ_id=categ_id, qty=qty,
            partner_id=partner_id)
        if pricelist_item_ids:
            pricelist_item_id = pricelist_item_ids[0]
        return pricelist_item_id

    @api.one
    def price_get(self, product_id, qty, partner_id, uom_id):
        product_obj = self.env['product.product']
        price_type_obj = self.env['product.price.type']
        product = product_obj.browse(product_id)
        price = False
        qty_uom_id = uom_id or product.uom_id.id
        price_uom_id = qty_uom_id
        price_types = {}
        if self.base == -1:
            if self.base_pricelist_id:
                price_tmp = self.base_pricelist_id._price_get_multi(
                    self.base_pricelist_id,
                    [(product, qty, False)])[product.id]
                ptype_src = self.base_pricelist_id.currency_id
                price = ptype_src.compute(
                    price_tmp, self.pricelist.currency_id, round=False)
        elif self.base == -2:
            partner_lst = product.supplier_ids
            if self.pricelist.type == 'sale':
                partner_lst = product.customer_ids
            seller = False
            for seller_id in partner_lst:
                if (not partner_id) or (seller_id.name.id != partner_id):
                    continue
                seller = seller_id
            if not seller and partner_lst:
                seller = partner_lst[0]
            if seller:
                qty_in_seller_uom = qty
                for line in seller.pricelist_ids:
                    if line.min_quantity <= qty_in_seller_uom:
                        price = line.price
        else:
            if self.base not in price_types:
                price_types[self.base] = price_type_obj.browse(int(self.base))
            price_type = price_types[self.base]
            # price_get returns the price in the context UoM, i.e.
            # qty_uom_id
            price = price_type.currency_id.compute(
                product.product_tmpl_id._price_get(
                    product, price_type.field)[product.id],
                self.pricelist.currency_id,
                round=False)
        if price is not False:
            price_limit = price
            price = price * (1.0+(self.price_discount or 0.0))
            if self.price_round:
                price = tools.float_round(
                    price, precision_rounding=self.price_round)
            convert_to_price_uom = (
                lambda price: product.uom_id._compute_price(
                    price_uom_id, price))
            if self.price_surcharge:
                price_surcharge = convert_to_price_uom(self.price_surcharge)
                price += price_surcharge
            if self.price_min_margin:
                price_min_margin = convert_to_price_uom(self.price_min_margin)
                price = max(price, price_limit + price_min_margin)
            if self.price_max_margin:
                price_max_margin = convert_to_price_uom(self.price_max_margin)
                price = min(price, price_limit + price_max_margin)
        # Final price conversion to target UoM
        uom_obj = self.env['product.uom']
        price = uom_obj._compute_price(price_uom_id, price, qty_uom_id)
        return price
