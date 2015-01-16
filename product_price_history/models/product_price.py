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

import logging
from openerp import models, fields, api

# All field name of product that will be historize
PRODUCT_FIELD_HISTORIZE = ['standard_price', 'cost_price']

_logger = logging.getLogger(__name__)


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    @api.one
    @api.depends('product', 'product_template_id')
    def _get_cost_type(self):
        if self.product:
            self.cost_type = 'product'
        else:
            self.cost_type = 'template'

    product = fields.Many2one(
        comodel_name='product.product', string='Product',
        ondelete='cascade')
    cost_type = fields.Selection(
        selection=[('template', 'Product'), ('product', 'Product Variant')],
        string='Cost Type', compute='_get_cost_type')

    @api.model
    def _get_historic_price(
            self, template_ids=None, product_ids=None, company_id=False,
            datetime=False, field_names=None):
        """ Use SQL for performance. Return a dict like:
            {product_id:{'standard_price': Value, 'list_price': Value}}
            If no value found, return 0.0 for each field and products.
        """
        cr = self.env.cr
        res = {}
        if not template_ids and not product_ids:
            return res
        if field_names is None:
            field_names = PRODUCT_FIELD_HISTORIZE
        if not datetime:
            datetime = fields.Datetime.now()
        if not company_id:
            company_id = (self.env.context.get('company_id', False) or
                          self.env.user.company_id.id)
        if template_ids:
            select = ("SELECT DISTINCT ON (product_template_id) "
                      "datetime, product_template_id AS product_id, cost ")
            table = "FROM product_price_history "
            where = ("WHERE product_template_id IN %s "
                     "AND product IS NULL "
                     "AND company_id = %s "
                     "AND datetime <= %s ")
            args = [tuple(template_ids),  company_id, datetime]
            # at end, sort by ID desc if several entries are created
            # on the same datetime
            order = ("ORDER BY product_template_id, datetime DESC, id DESC ")
            for id in template_ids:
                res[id] = dict.fromkeys(field_names, 0.0)
        elif product_ids:
            select = ("SELECT DISTINCT ON (product) "
                      "datetime, product AS product_id, cost ")
            table = "FROM product_price_history "
            where = ("WHERE product IN %s "
                     "AND company_id = %s "
                     "AND datetime <= %s ")
            args = [tuple(product_ids),  company_id, datetime]
            # at end, sort by ID desc if several entries are created
            # on the same datetime
            order = ("ORDER BY product, datetime DESC, id DESC ")
            for id in product_ids:
                res[id] = dict.fromkeys(field_names, 0.0)
        cr.execute(select + table + where + order, args)
        result = cr.dictfetchall()
        for line in result:
            data = dict.fromkeys(field_names, line['cost'])
            res[line['product_id']].update(data)
        _logger.debug("Result of price history is : %s, company_id: %s",
                      res, company_id)
        return res
