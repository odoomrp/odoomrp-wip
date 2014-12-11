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
    @api.model
    def generate_purchase_orders(self):
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        supplierinfo_obj = self.env['product.supplierinfo']
        for requisition in self:
            for line in requisition.line_ids:
                product = line.product_id
                condition = [('product_tmpl_id', '=',
                              product.product_tmpl_id.id)]
                supplierinfos = supplierinfo_obj.search(condition)
                if not supplierinfos:
                    raise exceptions.Warning(
                        _('You must define one supplier for the product: %s') %
                        product.name)
                else:
                    for supplierinfo in supplierinfos:
                        supplier = supplierinfo.name
                        try:
                            vals = self._prepare_purchase_order_line(
                                requisition, line, False, supplier)
                            condition = [('partner_id', '=', supplier.id),
                                         ('state', '=', 'draft'),
                                         ('requisition_id', '=',
                                          requisition.id)]
                            purchase_order = purchase_obj.search(condition)
                            if not purchase_order:
                                po_vals = self._prepare_purchase_order(
                                    requisition, supplier)
                                purchase = purchase_obj.create(po_vals)
                            else:
                                purchase = purchase_order[0]
                            vals.update({'order_id': purchase.id})
                            purchase_line_obj.create(vals)
                        except:
                            _logger.info(_('Supplier: %s - Product: %s') %
                                         (supplier.name, product.name))
        return True
