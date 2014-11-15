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

from openerp import models, fields, tools, api, exceptions, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.model
    def _price_rule_get_multi(self, pricelist, products_by_qty_by_partner):
        context = self.env.context.copy() or {}
        if 'price_extra' not in context:
            return super(ProductPricelist, self)._price_rule_get_multi(
                pricelist, products_by_qty_by_partner)
        date = context.get('date') or fields.Date.context_today(self)
        price_extra = context.get('price_extra')

        products = map(lambda x: x[0], products_by_qty_by_partner)
        product_uom_obj = self.env['product.uom']
        price_type_obj = self.env['product.price.type']

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if (((v.date_start is False) or (v.date_start <= date)) and
                    ((v.date_end is False) or (v.date_end >= date))):
                version = v
                break
        if not version:
            raise exceptions.Warning(_("At least one pricelist has no active"
                                       " version !\nPlease create or activate"
                                       " one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        prod_tmpl_ids = [tmpl.id for tmpl in products]

        # Load all rules
        cr = self.env.cr
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
            'AND (product_id IS NULL) '
            'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
            'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, categ_ids, version.id))
        item_ids = [x[0] for x in cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)

        price_types = {}
        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            uom_price_already_computed = False
            results[product.id] = 0.0
            price = False
            rule_id = False
            for rule in items:
                if rule.min_quantity and qty < rule.min_quantity:
                    continue
                if (rule.product_tmpl_id and
                        product.id != rule.product_tmpl_id.id):
                    continue
                if rule.product_id:
                    continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(
                            rule.base_pricelist_id,
                            [(product, qty, False)])[product.id]
                        uom_price_already_computed = True
                        price = pricelist.currency_id.compute(
                            price_tmp, pricelist.currency_id, round=False)
                elif rule.base == -2:
                    for seller in product.seller_ids:
                        if (not partner) or (seller.name.id != partner):
                            continue
                        qty_in_seller_uom = qty
                        from_uom = context.get('uom') or product.uom_id.id
                        seller_uom = (seller.product_uom and
                                      seller.product_uom.id or False)
                        if seller_uom and from_uom and from_uom != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(
                                from_uom, qty, to_uom_id=seller_uom)
                        else:
                            uom_price_already_computed = True
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(
                            int(rule.base))
                    price_type = price_types[rule.base]

                    uom_price_already_computed = True
                    price = price_type.currency_id.compute(
                        product._price_get([product],
                                           price_type.field)[product.id],
                        pricelist.currency_id,
                        round=False)

                if price is not False:
                    price += price_extra
                    price_limit = price
                    price = price * (1.0+(rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(
                            price, precision_rounding=rule.price_round)
                    price += (rule.price_surcharge or 0.0)
                    if rule.price_min_margin:
                        price = max(price, price_limit+rule.price_min_margin)
                    if rule.price_max_margin:
                        price = min(price, price_limit+rule.price_max_margin)
                    rule_id = rule.id
                break

            if price:
                if 'uom' in context and not uom_price_already_computed:
                    uom = product.uos_id or product.uom_id
                    price = uom._compute_price(price, context['uom'])

            results[product.id] = (price, rule_id)
        return results

    @api.multi
    def template_price_get(self, prod_id, qty, partner=None):
        return dict((key, price[0]) for key, price in
                    self.template_price_rule_get(prod_id, qty,
                                                 partner=partner).items())

    @api.multi
    def template_price_rule_get(self, prod_id, qty, partner=None):
        product = self.env['product.template'].browse(prod_id)
        res_multi = self.price_rule_get_multi(
            products_by_qty_by_partner=[(product, qty, partner)])
        res = res_multi[prod_id]
        return res
