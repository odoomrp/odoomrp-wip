# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class MrpWorkOrderProduce(models.TransientModel):
    _inherit = "mrp.work.order.produce"

    @api.model
    def default_get(self, var_fields):
        operation_obj = self.env['mrp.production.workcenter.line']
        res = super(MrpWorkOrderProduce, self).default_get(var_fields)
        operation = operation_obj.browse(self.env.context['active_id'])
        accepted_amount = sum(
            x.accepted_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'processed'))
        res['product_qty'] = (operation.production_id.product_qty -
                              accepted_amount)
        return res

    @api.multi
    def on_change_qty(self, product_qty, consume_lines):
        operation_obj = self.env['mrp.production.workcenter.line']
        planned_product_obj = self.env['mrp.production.product.line']
        res = super(MrpWorkOrderProduce, self).on_change_qty(product_qty,
                                                             consume_lines)
        operation = operation_obj.browse(self.env.context['active_id'])
        accepted_amount = sum(
            x.accepted_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'pending'))
        rejected_amount = sum(
            x.rejected_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'pending'))
        for line in res['value']['consume_lines']:
            cond = [('work_order', '=', operation.id),
                    ('product_id', '=', line[2].get('product_id'))]
            planned_product = planned_product_obj.search(cond, limit=1)
            factor = (planned_product.product_qty /
                      operation.production_id.product_qty)
            line[2]['product_qty'] = ((factor * accepted_amount) +
                                      (factor * rejected_amount))
        return res

    @api.multi
    def do_consume(self):
        res = super(MrpWorkOrderProduce, self).do_consume()
        self._update_operation_time_lines()
        return res

    @api.multi
    def do_consume_produce(self):
        res = super(MrpWorkOrderProduce, self).do_consume_produce()
        self._update_operation_time_lines()
        return res

    def _update_operation_time_lines(self):
        operation_obj = self.env['mrp.production.workcenter.line']
        operation = operation_obj.browse(self.env.context['active_id'])
        time_lines = operation.operation_time_lines.filtered(
            lambda r: r.state == 'pending')
        time_lines.write({'state': 'processed'})
