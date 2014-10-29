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
from openerp import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def wkf_approve_order(self):
        res = super(PurchaseOrder, self).wkf_approve_order()
        for po in self:
            for line in po.order_line:
                if line.product_id:
                    vals = {'last_purchase_date': fields.Datetime.now(),
                            'last_supplier_id': line.order_id.partner_id.id,
                            'last_purchase_price': line.price_unit
                            }
                    line.product_id.write(vals)
        return res
