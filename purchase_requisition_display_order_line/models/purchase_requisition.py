# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import logging
from openerp import models, api

_logger = logging.getLogger(__name__)


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def open_purchase_lines(self):
        template_obj = self.env['product.template']
        result = template_obj._get_act_window_dict(
            'purchase_requisition_display_order_line.action_open_purchase_line'
            '_from_displayorderline')
        po_line_ids = [po_line.id for po_line in self.po_line_ids]
        result['domain'] = [('id', 'in', po_line_ids)]
        return result
