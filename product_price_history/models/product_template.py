# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api

from .product_price import PRODUCT_FIELD_HISTORIZE


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def open_product_historic_prices(self):
        res = self.env['ir.actions.act_window'].for_xml_id(
            'product_price_history', 'action_tmpl_price_history')
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
