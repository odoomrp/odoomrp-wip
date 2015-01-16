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

from openerp import models, api

from .product_price import PRODUCT_FIELD_HISTORIZE


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def open_product_historic_prices(self):
        res = self.env['ir.actions.act_window'].for_xml_id(
            'product_price_history', 'action_price_history')
        res['domain'] = ((res.get('domain', []) or []) +
                         [('product_template_id', 'in', self.ids)])
        return res

    @api.multi
    def read(self, fields, load='_classic_read'):
        if fields:
            fields.append('id')
        results = super(ProductTemplate, self).read(fields, load=load)
        # Note if fields is empty => read all, so look at history table
        if not fields or any([f in PRODUCT_FIELD_HISTORIZE for f in fields]):
            p_history = self.env['product.price.history']
            company_id = (self.env.context.get('company_id', False) or
                          self.env.user.company_id.id)
            # if fields is empty we read all price fields
            if not fields:
                p_fields = PRODUCT_FIELD_HISTORIZE
            # Otherwise we filter on price fields asked in read
            else:
                p_fields = [f for f in PRODUCT_FIELD_HISTORIZE if f in fields]
            prod_prices = p_history._get_historic_price(
                template_ids=self.ids, company_id=company_id,
                datetime=self.env.context.get('to_date', False),
                field_names=p_fields)
            if prod_prices:
                for result in results:
                    dict_value = prod_prices[result['id']]
                    result.update(dict_value)
        return results
