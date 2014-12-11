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

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    cost_price = fields.Float(
        string="Variant Cost Price", digits=dp.get_precision('Product Price'),
        groups="base.group_user", company_dependent=True)

    @api.one
    def _set_cost_price(self, value):
        ''' Store the cost price change in order to be able to retrieve the
        cost of a product for a given date'''
        price_history_obj = self.env['product.price.history']
        user_company = self.env.user.company_id.id
        company_id = self.env.context.get('force_company', user_company)
        price_history_obj.create({
            'product_template_id': self.product_tmpl_id.id,
            'product': self.id,
            'cost': value,
            'company_id': company_id,
        })

    @api.model
    def create(self, values):
        product = super(ProductProduct, self).create(values)
        product._set_cost_price(values.get('cost_price', 0.0))
        return product

    @api.multi
    def write(self, values):
        if 'cost_price' in values:
            for product in self:
                product._set_cost_price(values['cost_price'])
        return super(ProductProduct, self).write(values)

    @api.multi
    def open_product_historic_prices(self):
        res = super(ProductProduct, self).open_product_historic_prices()
        res['domain'] = ((res.get('domain', []) or []) +
                         [('product', 'in', self.ids)])
        return res


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    product = fields.Many2one(
        comodel_name='product.product', string='Product',
        ondelete='cascade')
