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

from openerp import fields, models, api


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    @api.multi
    def _get_variant_inventory_value(self):
        self.ensure_one()
        if self.product_id.cost_method in ('real'):
            return self.cost * self.qty
        return self.product_id.cost_price * self.qty

    @api.one
    @api.depends("product_id", "product_id.cost_price", "qty",
                 "product_id.cost_method")
    def _calc_variant_inventory_value(self):
        self.variant_inventory_value = self.with_context(
            force_company=self.company_id.id)._get_variant_inventory_value()

    variant_inventory_value = fields.Float(
        string="Inventory Value", store=True,
        compute="_calc_variant_inventory_value", )


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def _store_average_cost_price(self, move):
        ''' move is a browse record '''
        res = super(StockMove, self)._store_average_cost_price(move)
        if any([q.qty <= 0 for q in move.quant_ids]):
            return
        average_valuation_price = 0.0
        for q in move.quant_ids:
            average_valuation_price += q.qty * q.cost
        average_valuation_price = average_valuation_price / move.product_qty
        product = move.product_id
        product.sudo().write({'cost_price': average_valuation_price})
        return res

    @api.multi
    def product_price_update_before_done(self):
        for move in self:
            if ((move.location_id.usage == 'supplier') and
                    (move.product_id.cost_method == 'average')):
                product = move.product_id
                product_avail = move.product_id.qty_available
                new_std_price = 0
                if product_avail <= 0:
                    new_std_price = move.price_unit
                else:
                    amount_unit = product.cost_price
                    new_std_price = (((amount_unit * product_avail) +
                                     (move.price_unit * move.product_qty)) /
                                     (product_avail + move.product_qty))
                product.sudo().write({'cost_price': new_std_price})
