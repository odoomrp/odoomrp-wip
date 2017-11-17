# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class MrpWorkOrderProduce(models.TransientModel):
    _inherit = "mrp.work.order.produce"

    qty_to_produce = fields.Integer(string='Quantity to produce')
    accepted_amount = fields.Integer(string='Accepted amount')
    pending_accepted_amount = fields.Integer(
        string='Pending accepted amount')
    pending_rejected_amount = fields.Integer(
        string='Pending rejected amount')
    pending_total_amount = fields.Integer(
        string='Pending total amount')
    confirmed_accepted_amount = fields.Integer(
        string='Confirmed accepted amount')
    confirmed_rejected_amount = fields.Integer(
        string='Confirmed rejected amount')
    confirmed_total_amount = fields.Integer(
        string='Confirmed total amount')
    total_amount = fields.Integer(string='Total amount')

    @api.model
    def default_get(self, var_fields):
        operation_obj = self.env['mrp.production.workcenter.line']
        res = super(MrpWorkOrderProduce, self).default_get(var_fields)
        operation = operation_obj.browse(self.env.context.get('active_id'))
        accepted_amount = sum(
            x.accepted_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'processed'))
        pending_accepted_amount = sum(
            x.accepted_amount for x in operation.operation_time_lines.filtered(
                lambda r: r.state == 'pending'))
        pending_rejected_amount = sum(
            x.rejected_amount for x in operation.operation_time_lines.filtered(
                lambda r: r.state == 'pending'))
        confirmed_rejected_amount = sum(
            x.rejected_amount for x in operation.operation_time_lines.filtered(
                lambda r: r.state == 'processed'))
        res.update({'product_qty': pending_accepted_amount,
                    'qty_to_produce': operation.production_id.product_qty,
                    'accepted_amount': accepted_amount,
                    'pending_accepted_amount': pending_accepted_amount,
                    'pending_rejected_amount': pending_rejected_amount,
                    'pending_total_amount': (pending_accepted_amount +
                                             pending_rejected_amount),
                    'confirmed_accepted_amount': accepted_amount,
                    'confirmed_rejected_amount': confirmed_rejected_amount,
                    'confirmed_total_amount': (accepted_amount +
                                               confirmed_rejected_amount),
                    'total_amount': (
                        pending_accepted_amount + pending_rejected_amount +
                        accepted_amount + confirmed_rejected_amount)})
        return res

    @api.multi
    def on_change_qty(self, product_qty, consume_lines):
        operation_obj = self.env['mrp.production.workcenter.line']
        planned_product_obj = self.env['mrp.production.product.line']
        operation = operation_obj.browse(self.env.context.get('active_id'))
        processed_accepted_amount = sum(
            x.accepted_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'processed'))
        res = super(MrpWorkOrderProduce, self).on_change_qty(
            operation.production_id.product_qty - processed_accepted_amount,
            consume_lines)
        accepted_amount = sum(
            x.accepted_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'pending'))
        rejected_amount = sum(
            x.rejected_amount for x in
            operation.operation_time_lines.filtered(
                lambda r: r.state == 'pending'))
        if (product_qty + processed_accepted_amount >
                operation.production_id.product_qty):
            res['warning'] = {
                'title': _('Product to produce'),
                'message': _('Quantity to produce greater than planned')}
        if (not res.get('value', False) or
            (res.get('value', False) and not
             res['value'].get('consume_lines',
                              False)) or res['value']['consume_lines'] == []):
            res['value']['consume_lines'] = self._catch_consume_lines(
                operation)
        for line in res['value']['consume_lines']:
            cond = [('work_order', '=', operation.id),
                    ('product_id', '=', line[2].get('product_id'))]
            planned_product = planned_product_obj.search(cond, limit=1)
            factor = (planned_product.product_qty /
                      operation.production_id.product_qty)
            line[2]['qty_to_produce'] = operation.production_id.product_qty
            line[2]['planned_qty'] = planned_product.product_qty
            line[2]['factor'] = factor
            line[2]['product_qty'] = ((factor * accepted_amount) +
                                      (factor * rejected_amount))
            line[2]['accepted_amount'] = accepted_amount
            line[2]['rejected_amount'] = rejected_amount
        return res

    def _catch_consume_lines(self, operation):
        consume_lines = []
        for line in operation.product_line:
            consume_lines.append(
                [0, False, {'lot_id': False,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_qty}])
        return consume_lines

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


class MrpProductProduceLine(models.TransientModel):
    _inherit = "mrp.product.produce.line"

    qty_to_produce = fields.Integer(string='Quantity to produce')
    planned_qty = fields.Integer(string='Planned quantity to consume')
    factor = fields.Float(string='Factor')
    accepted_amount = fields.Integer(string='Accepted amount')
    rejected_amount = fields.Integer(string='Rejected amount')
