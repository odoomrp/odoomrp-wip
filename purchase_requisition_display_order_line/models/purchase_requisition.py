# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import logging

from openerp import models, api, exceptions
from openerp import _

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
        result['domain'] = "[('id', 'in', " + str(po_line_ids) + ")]"
        return result
