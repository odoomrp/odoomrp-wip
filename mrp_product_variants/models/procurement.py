# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, procurement):
        result = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        product_id = result.get('product_id')
        product = self.env['product.product'].browse(product_id)
        result['product_tmpl_id'] = product.product_tmpl_id.id
        product_attribute_ids = product._get_product_attributes_values_dict()
        result['product_attribute_ids'] = map(
            lambda x: (0, 0, x), product_attribute_ids)
        for val in result['product_attribute_ids']:
            val = val[2]
            val['product_tmpl_id'] = product.product_tmpl_id.id
            val['owner_model'] = 'mrp.production'
        return result
