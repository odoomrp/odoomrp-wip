# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class OperationTimeLine(models.Model):
    _inherit = 'operation.time.line'

    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee', readonly=True)
    accepted_amount = fields.Integer(
        string='Accepted amount', default=0)
    rejected_amount = fields.Integer(
        string='Rejected amount', default=0)
    state = fields.Selection(
        [('pending', 'Pending'),
         ('processed', 'Processed'),
         ('canceled', 'Canceled')
         ], string="State", default='pending', required=True)
