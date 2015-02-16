# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class BidLineQty(models.TransientModel):
    _inherit = "bid.line.qty"

    @api.multi
    def change_qty(self):
        self.ensure_one()
        purchase_line_obj = self.env['purchase.order.line']
        if ('active_ids' in self._context and
                self._context.get('active_model') == 'purchase.order.line'):
            active_ids = self._context['active_ids']
            for line in purchase_line_obj.browse(active_ids):
                line.write({'product_qty': self.qty})
                return True
        else:
            return super(BidLineQty, self).change_qty()
