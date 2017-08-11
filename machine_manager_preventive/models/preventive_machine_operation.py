# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError
from dateutil.relativedelta import relativedelta


class PreventiveMachineOperation(models.Model):
    _name = "preventive.machine.operation"
    _description = "Preventive operation for machine."

    @api.multi
    @api.depends('cycles', 'lastcycles')
    def _compute_next_cycles(self):
        for record in self.filtered('cycles'):
            record.nextcycles = record.lastcycles + record.cycles

    @api.multi
    @api.depends('lastdate', 'frequency', 'interval_unit')
    def _compute_next_date(self):
        for record in self.filtered(lambda x: x.lastdate and x.frequency and
                                    x.interval_unit):
            record.nextdate = self.get_interval_date(
                record.lastdate, record.frequency, record.interval_unit)

    @api.multi
    @api.depends('repair_order_ids', 'repair_order_ids.state')
    def _compute_active_repair_order(self):
        for record in self:
            if record.repair_order_ids.filtered(
                    lambda o: o.state in ('draft', 'confirmed', 'ready')):
                record.active_repair_order = True
            else:
                record.active_repair_order = False

    name = fields.Char(string='REF', required=True)
    opdescription = fields.Text(string='Description')
    machine = fields.Many2one(comodel_name='machinery', string='Machine',
                              required=True, readonly=True)
    opname_omm = fields.Many2one(comodel_name='preventive.operation.matmach',
                                 string='Operation Material Machine',
                                 required=True, readonly=True)
    frequency = fields.Integer(string='Frequency',
                               help="Estimated time for the next operation.")
    interval_unit = fields.Selection(
        selection=[('day', 'Days'), ('week', 'Weeks'), ('mon', 'Months'),
                   ('year', 'Years')], string='Interval unit')
    cycles = fields.Integer(string='Op. Cycles Increment',
                            help="Cycles increment for the next operation.")
    lastdate = fields.Date(string='Date',
                           help="Last date on which the operation was done.")
    lastcycles = fields.Integer(
        string='Cycles', help="Cycles of the machine on last operation.")
    last_hours_qty = fields.Float(string='Last Quantity Hours', required=False,
                                  help="Time takes to do the operation. hh:mm")
    nextcycles = fields.Integer(
        string='Cycles', compute="_compute_next_cycles",
        help="Cycles of the machine for next operation.")
    nextdate = fields.Date(string='Date', compute="_compute_next_date",
                           help="Expected date for next operation.",
                           store=True)
    hours_qty = fields.Float(
        string='Quantity Hours', required=False,
        help="Expected time for execution the operation. hh:mm")
    alert = fields.Boolean(string='1st alert')
    extra_alert = fields.Boolean(string='2nd alert')
    check_al1 = fields.Boolean(
        string='1st alert check', help="If checked the alarm will be test at"
        " the specified parameters.")
    check_al2 = fields.Boolean(
        string='2nd alert check', help="If checked the alarm will be test at"
        " the specified parameters.")
    first_margin = fields.Integer(
        string='First Cycle Margin', help="A negative number means that the"
        " alarm will be activated before the condition is met")
    second_margin = fields.Integer(
        string='Second Cycle Margin', help="A negative number means that the"
        " alarm will be activated before the condition is met")
    margin_fre1 = fields.Integer(
        string='Frequency Margin', help="A negative number means that the"
        " alarm will be activated before the compliance date")
    interval_unit1 = fields.Selection(
        selection=[('day', 'Days'), ('week', 'Weeks'), ('mon', 'Months'),
                   ('year', 'Years')], string='Interval Unit')
    margin_fre2 = fields.Integer(
        string='Frequency Margin', help="A negative number means that the"
        " alarm will be activated before the compliance date")
    interval_unit2 = fields.Selection(
        selection=[('day', 'Days'), ('week', 'Weeks'), ('mon', 'Months'),
                   ('year', 'Years')], string='Interval Unit')
    update_preventive = fields.Selection(
        related='opname_omm.update_preventive')
    actcycles = fields.Integer(related='machine.actcycles')
    repair_order_ids = fields.Many2many(comodel_name='mrp.repair')
    active_repair_order = fields.Boolean(
        string='Active Repair', store=True,
        compute="_compute_active_repair_order")

    @api.constrains('first_margin', 'second_margin')
    def _check_cycle_margins(self):
        for record in self:
            if record.first_margin and record.second_margin and(
                    record.first_margin > record.second_margin):
                raise ValidationError(
                    _("First margin must be before second"))

    @api.constrains('margin_fre1', 'interval_unit1', 'margin_fre2',
                    'interval_unit2')
    def _check_time_margins(self):
        for record in self:
            if record.interval_unit1 and record.interval_unit2:
                date = fields.Date.today()
                margin1 = self.get_interval_date(date, record.margin_fre1,
                                                 record.interval_unit1)
                margin2 = self.get_interval_date(date, record.margin_fre2,
                                                 record.interval_unit2)
                if margin1 > margin2:
                    raise ValidationError(
                        _("First margin must be before second"))

    @api.one
    def set_alarm1(self):
        self.check_al1 = not self.check_al1

    @api.one
    def set_alarm2(self):
        self.check_al2 = not self.check_al2

    @api.onchange('actcycles')
    def _onchange_cycles_alert(self):
        if self.cycles > 0:
            res = self._check_alert_by_cycles(self)
            if not self.alert and res and res['alert']:
                self.alert = True
            if not self.extra_alert and res and res['extra_alert']:
                self.extra_alert = True

    @api.multi
    def _check_alert_by_cycles(self, operation):
        """ Raise alerts by cycles
        @param operation: Preventive operation for machine to check
        @return: Alert Raise
        """
        cycles = operation.actcycles
        margin1 = operation.nextcycles + operation.first_margin
        margin2 = operation.nextcycles + operation.second_margin
        res = {'alert': False, 'extra_alert': False}
        if cycles >= margin1 and operation.check_al1:
            res['alert'] = True
        if cycles >= margin2 and operation.check_al2:
            res['extra_alert'] = True
        return res

    @api.multi
    def _check_alert_by_time(self, operation):
        """ Creates an alert by time
        @param operation: Preventive operation for machine to check
        @return: Alert Raise
        """
        date = fields.Date.today()
        op_date = (operation.nextdate or operation.lastdate or
                   operation.machine.enrolldate or date)
        freq1 = self.get_interval_date(op_date, operation.margin_fre1,
                                       operation.interval_unit1)
        freq2 = self.get_interval_date(op_date, operation.margin_fre2,
                                       operation.interval_unit2)
        res = {'alert': False, 'extra_alert': False}
        if (date >= freq1 and operation.check_al1):
            res['alert'] = True
        if (date >= freq2 and operation.check_al2):
            res['extra_alert'] = True
        return res

    def get_interval_date(self, date, interval, interval_unit=False):
        """ Returns Interval date for current values
        @param date: Date from interval calculation (string)
        @param interval: Interval number
        @param interval_unit: Unit of interval measure (day-week-mon or year)
        @return: Calculated interval date
        """
        if interval_unit == 'day':
            inter_date = fields.Date.from_string(date) + (
                relativedelta(days=interval))
        elif interval_unit == 'week':
            inter_date = fields.Date.from_string(date) + (
                relativedelta(weeks=interval))
        elif interval_unit == 'mon':
            inter_date = fields.Date.from_string(date) + (
                relativedelta(months=interval))
        else:
            inter_date = fields.Date.from_string(date) + (
                relativedelta(years=interval))
        return fields.Date.to_string(inter_date)

    @api.multi
    def check_alerts(self):
        records = self.search([])
        for ope in records:  # Loop for all operations
            res1 = False
            res2 = False
            if ope.cycles > 0:
                res1 = self._check_alert_by_cycles(ope)
            if ope.frequency > 0:
                res2 = self._check_alert_by_time(ope)
            ope.alert = (res1 and res1['alert'] or
                         res2 and res2['alert'] or False)
            ope.extra_alert = (res1 and res1['extra_alert'] or
                               res2 and res2['extra_alert'] or False)

    @api.multi
    def show_attachments(self):
        document_obj = self.env['ir.attachment']
        self.ensure_one()
        attachments = document_obj.search(
            [('res_model', '=', 'preventive.operation.type'),
             ('res_id', '=', self.opname_omm.optype_id.id)])
        search_view = self.env.ref('base.view_attachment_search')
        idform = self.env.ref('base.view_attachment_form')
        idtree = self.env.ref('base.view_attachment_tree')
        kanban = self.env.ref('mail.view_document_file_kanban')
        return {
            'view_type': 'form',
            'view_mode': 'kanban, tree, form',
            'res_model': 'ir.attachment',
            'views': [(kanban.id, 'kanban'), (idtree.id, 'tree'),
                      (idform.id, 'form')],
            'search_view_id': search_view.id,
            'view_id': kanban.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', attachments.ids)],
            'context': self.env.context,
            }

    @api.multi
    def _next_action_update(self):
        for op_pmo in self:
            if op_pmo.cycles:
                op_pmo.lastcycles = op_pmo.actcycles
            if op_pmo.interval_unit:
                op_pmo.lastdate = fields.Date.today()
        self.check_alerts()

    @api.multi
    def create_repair_order(self):
        self.ensure_one()
        if self.active_repair_order is False:
            raise UserError(
                _('Repair order done, please refresh view'))
        preventive_repair_obj = self.env['preventive.repair.order']
        preventive_repair_obj.with_context(
            active_ids=[self.id]).create_repair_from_pmo()
