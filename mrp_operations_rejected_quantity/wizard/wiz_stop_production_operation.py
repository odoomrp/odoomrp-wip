# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class WizStopProductionOperation(models.TransientModel):
    _name = 'wiz.stop.production.operation'

    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee')
    accepted_amount = fields.Integer(
        string='Accepted amount', default=0)
    rejected_amount = fields.Integer(
        string='Rejected amount', default=0)
    stop_date = fields.Datetime(
        string='Date stop', default=fields.Datetime.now)

    @api.model
    def default_get(self, var_fields):
        operation_obj = self.env['mrp.production.workcenter.line']
        res = super(WizStopProductionOperation, self).default_get(var_fields)
        operation = operation_obj.browse(self.env.context.get('active_id'))
        res['accepted_amount'] = (operation.production_id.product_qty -
                                  sum(x.accepted_amount for x in
                                      operation.operation_time_lines.filtered(
                                          lambda r: r.state == 'processed')))
        return res

    @api.multi
    def stop_operation(self):
        operation_obj = self.env['mrp.production.workcenter.line']
        operation = operation_obj.browse(self.env.context.get('active_id'))
        operation_time = operation.operation_time_lines.filtered(
            lambda x: not x.end_date)
        operation_time.write({'employee_id': self.employee_id.id,
                              'accepted_amount': self.accepted_amount,
                              'rejected_amount': self.rejected_amount,
                              'end_date': self.stop_date})
        operation.signal_workflow('button_pause')
