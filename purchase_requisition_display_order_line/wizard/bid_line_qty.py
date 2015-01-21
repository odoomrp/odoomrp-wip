# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class BidLineQty(models.TransientModel):
    _inherit = "bid.line.qty"

    @api.one
    def change_qty(self):
        purchase_line_obj = self.env['purchase.order.line']
        if 'active_ids' in self._context:
            active_ids = self._context['active_ids']
            for line in purchase_line_obj.browse(active_ids):
                line.write({'product_qty': self.qty})
        return {'type': 'ir.actions.act_window_close'}
