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

    mrp_operation = fields.Many2one(
        'mrp.production.workcenter.line', 'MPR Operation')

    @api.multi
    def make_po(self):
        purchase_line_obj = self.env['purchase.order.line']
        res = super(ProcurementOrder, self).make_po()
        for procurement in self:
            if res[procurement.id]:
                purchase_line = purchase_line_obj.browse(res[procurement.id])
                if (procurement.mrp_operation and
                    (not purchase_line.order_id.mrp_operation or
                     procurement.mrp_operation.id !=
                     purchase_line.order_id.mrp_operation.id)):
                    purchase_line.order_id.update(
                        {'mrp_operation': procurement.mrp_operation.id})
                    procurement.mrp_operation.update(
                        {'purchase_order': purchase_line.order_id.id})
        return res
