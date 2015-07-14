# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def write(self, values):
        res = super(ProcurementOrder, self).write(values)
        if 'purchase_line_id' in values:
            for proc in self:
                if (proc.service_sale_line_id and
                    proc.service_sale_line_id.delivery_standard_price and
                        proc.purchase_line_id):
                    name = proc.purchase_line_id.name
                    name += ', ' + proc.origin + ', ' + str(proc.date_planned)
                    proc.purchase_line_id.write(
                        {'name': name,
                         'price_unit':
                         proc.service_sale_line_id.delivery_standard_price})
        return res
