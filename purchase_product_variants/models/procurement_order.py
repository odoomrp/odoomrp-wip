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
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_template'] = product.product_tmpl_id.id
        return vals
