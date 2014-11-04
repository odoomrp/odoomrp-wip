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
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    plan = fields.Many2one('procurement.plan', string='Plan')

    @api.model
    def _prepare_orderpoint_procurement2(self, orderpoint, product_qty):
        result = super(ProcurementOrder, self)._prepare_orderpoint_procurement(
            orderpoint, product_qty)
        if 'plan' in self.env.context:
            result.update({'plan': self.env.context.get('plan')})
        return result

    @api.model
    def create(self, data):
        if 'plan' in self.env.context and 'plan' not in data:
            data.update({'plan': self.env.context.get('plan')})
        procurement = super(ProcurementOrder, self).create(data)
        return procurement

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        purchase_obj = self.env['purchase.order']
        pur = super(ProcurementOrder, self).create_procurement_purchase_order(
            cr, uid, procurement, po_vals, line_vals, context=context)
        if procurement.plan:
            vals = {'plan': procurement.plan.id}
            purchase_obj.write(cr, uid, [pur], vals, context=context)
        return pur
