# -*- coding: utf-8 -*-
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _get_po_line_values_from_proc(self, procurement, partner, company,
                                      schedule_date):
        """Write also the product template in the created purchase order."""
        vals = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        if vals.get('product_id'):
            ctx = self._context.copy()
            if partner:
                ctx.update({'lang': partner.lang, 'partner_id': partner.id})
            product = self.env['product.product'].with_context(ctx).browse(
                vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id
            vals['product_attribute_ids'] = \
                [(0, 0, x) for x in
                 product._get_product_attributes_values_dict()]
            for val in vals['product_attribute_ids']:
                val = val[2]
                val['product_tmpl_id'] = product.product_tmpl_id.id
                val['owner_model'] = 'purchase.order.line'
            vals['name'] = self.env[
                'purchase.order.line']._get_product_description(
                product.product_tmpl_id, product, product.attribute_value_ids)
        return vals
