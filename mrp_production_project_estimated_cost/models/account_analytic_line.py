# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields
import openerp.addons.decimal_precision as dp


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    estim_standard_cost = fields.Float(
        string='Estimate Standard Cost',
        digits=dp.get_precision('Product Price'))
    estim_average_cost = fields.Float(
        string='Estimate Average Cost',
        digits=dp.get_precision('Product Price'))
    last_purchase_cost = fields.Float(
        string='Last Purchase Cost',
        digits=dp.get_precision('Product Price'))
    last_sale_price = fields.Float(
        string='Last Sale Price',
        digits=dp.get_precision('Product Price'))

    def on_change_unit_amount(self, cr, uid, ids, prod_id, quantity,
                              company_id, unit=False, journal_id=False,
                              context=None):
        product_obj = self.pool['product.product']
        result = super(AccountAnalyticLine, self).on_change_unit_amount(
            cr, uid, ids, prod_id, quantity, company_id, unit=unit,
            journal_id=journal_id, context=context)
        if prod_id:
            product = product_obj.browse(cr, uid, prod_id, context=context)
            value = result.get('value')
            value.update({'estim_standard_cost': product.manual_standard_cost,
                          'estim_average_cost': product.standard_price,
                          'last_purchase_cost': product.last_purchase_price,
                          'last_sale_price': product.last_sale_price})
            result.update({'value': value})
        return result
