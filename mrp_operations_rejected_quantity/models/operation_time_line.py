# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class OperationTimeLine(models.Model):
    _inherit = 'operation.time.line'

    @api.depends('accepted_amount', 'rejected_amount')
    @api.multi
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = line.accepted_amount + line.rejected_amount

    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee', readonly=True)
    accepted_amount = fields.Integer(
        string='Accepted amount', default=0)
    rejected_amount = fields.Integer(
        string='Rejected amount', default=0)
    total_amount = fields.Integer(
        string='Total amount', default=0, compute='_compute_total_amount')
    state = fields.Selection(
        [('pending', 'Pending'),
         ('processed', 'Processed'),
         ('canceled', 'Canceled')
         ], string="State", default='pending', required=True)
