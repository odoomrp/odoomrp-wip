# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.depends('operation_time_lines', 'operation_time_lines.state',
                 'operation_time_lines.rejected_amount', 'qty', 'hour',
                 'operation_time_lines.accepted_amount',
                 'operation_time_lines.uptime')
    @api.multi
    def _compute_real_hours(self):
        for workcenter_line in self:
            accepted = sum(workcenter_line.operation_time_lines.filtered(
                lambda r: r.state == 'processed').mapped('accepted_amount'))
            rejected = sum(workcenter_line.operation_time_lines.filtered(
                lambda r: r.state == 'processed').mapped('rejected_amount'))
            uptime = sum(workcenter_line.operation_time_lines.filtered(
                lambda r: r.state == 'processed').mapped('uptime'))
            workcenter_line.real_hours = uptime
            if workcenter_line.qty:
                workcenter_line.estimated_hours_recalculated = (
                    ((accepted + rejected) * workcenter_line.hour) /
                    workcenter_line.qty)
                workcenter_line.difference_between_hours = (
                    workcenter_line.real_hours -
                    workcenter_line.estimated_hours_recalculated)

    estimated_hours_recalculated = fields.Float(
        string='Estimated hours recalculated', compute='_compute_real_hours',
        store=True)
    real_hours = fields.Float(
        string='Real hours', compute='_compute_real_hours', digits=(12, 6),
        store=True)
    difference_between_hours = fields.Float(
        string='Difference between hours', compute='_compute_real_hours',
        digits=(12, 6), store=True)
