# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    service_sale_line_id = fields.Many2one(
        'sale.order.line', string='Sale order line')

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if procurement.product_id.type != 'service' or res:
            return res
        rule_id = self._find_suitable_rule(procurement)
        if rule_id:
            procurement.write({'rule_id': rule_id})
            return True
        return False
