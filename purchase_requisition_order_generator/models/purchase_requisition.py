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

from openerp import models, api, exceptions
from openerp.tools.translate import _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    @api.model
    def make_purchase_order_avanzosc(self):
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        partner_obj = self.env['res.partner']
        supplierinfo_obj = self.env['product.supplierinfo']
        res = {}
        for requisition in self:
            purchase_order_datas = []
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
                        condition = [('partner_id', '=', supplier.id),
                                     ('state', '=', 'draft'),
                                     ('requisition_id', '=', requisition.id)]
                        purchase_order = purchase_obj.search(condition)
                        if not purchase_order:
                            vals = self._prepare_purchase_order(requisition,
                                                                supplier)
                            purchase = purchase_obj.create(vals)
                            purchase_order_datas.append(purchase)
                        else:
                            purchase = purchase_order[0]
                        vals = self._prepare_purchase_order_line(requisition, line, purchase.id, supplier)
                        purchase_line_obj.create(vals)
            res[requisition.id] = purchase_order_datas
        return True
