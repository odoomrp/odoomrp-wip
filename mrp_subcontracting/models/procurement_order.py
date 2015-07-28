# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    mrp_operation = fields.Many2one(
        'mrp.production.workcenter.line', 'MRP Operation')

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
                    purchase_line.order_id.mrp_operation = (
                        procurement.mrp_operation.id)
                    procurement.mrp_operation.purchase_order = (
                        purchase_line.order_id.id)
        return res
