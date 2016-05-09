# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from openerp import models, fields, api

# All field name of product that will be historize
PRODUCT_FIELD_HISTORIZE = ['standard_price']

_logger = logging.getLogger(__name__)


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

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
                     "AND company_id = %s "
                     "AND datetime <= %s ")
            args = [tuple(template_ids),  company_id, datetime]
            # at end, sort by ID desc if several entries are created
            # on the same datetime
            order = ("ORDER BY product_template_id, datetime DESC, id DESC ")
            for id in template_ids:
                res[id] = dict.fromkeys(field_names, 0.0)
        elif product_ids:
            select = ("SELECT DISTINCT ON (product_id) "
                      "datetime, product_id AS product_id, cost ")
            table = "FROM product_price_history_product "
            where = ("WHERE product_id IN %s "
                     "AND company_id = %s "
                     "AND datetime <= %s ")
            args = [tuple(product_ids),  company_id, datetime]
            # at end, sort by ID desc if several entries are created
            # on the same datetime
            order = ("ORDER BY product_id, datetime DESC, id DESC ")
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


class ProductPriceHistoryProduct(models.Model):
    _inherit = 'product.price.history.product'

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
                     "AND company_id = %s "
                     "AND datetime <= %s ")
            args = [tuple(template_ids),  company_id, datetime]
            # at end, sort by ID desc if several entries are created
            # on the same datetime
            order = ("ORDER BY product_template_id, datetime DESC, id DESC ")
            for id in template_ids:
                res[id] = dict.fromkeys(field_names, 0.0)
        elif product_ids:
            select = ("SELECT DISTINCT ON (product_id) "
                      "datetime, product_id AS product_id, cost ")
            table = "FROM product_price_history_product "
            where = ("WHERE product_id IN %s "
                     "AND company_id = %s "
                     "AND datetime <= %s ")
            args = [tuple(product_ids),  company_id, datetime]
            # at end, sort by ID desc if several entries are created
            # on the same datetime
            order = ("ORDER BY product_id, datetime DESC, id DESC ")
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
