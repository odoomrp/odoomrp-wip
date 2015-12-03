# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta


class PreventiveMachineOperation(models.Model):
    _name = "preventive.machine.operation"
    _description = "Preventive operation for machine."

    @api.one
    def _next_cycles(self):
        if self and self.cycles:
            self.nextcycles = self.lastcycles + self.cycles

    name = fields.Char('REF', required=True)
    opdescription = fields.Text('Description')
    machine = fields.Many2one('machinery', 'Machine', required=True,
                              readonly=True)
    opname_omm = fields.Many2one('preventive.operation.matmach',
                                 'Operation Material Machine', required=True,
                                 readonly=True)
    frequency = fields.Integer('Frequency',
                               help="Estimated time for the next operation.")
    interval_unit = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                      ('mon', 'Months'), ('year', 'Years')],
                                     'Interval unit')
    cycles = fields.Integer('Op. Cycles Increment',
                            help="Cycles increment for the next operation.")
    lastdate = fields.Date('Date',
                           help="Last date on which the operation was done.")
    lastcycles = fields.Integer(
        'Cycles', help="Cycles of the machine on last operation.")
    last_hours_qty = fields.Float('Last Quantity Hours', required=False,
                                  help="Time takes to do the operation. hh:mm")
    nextcycles = fields.Integer('Cycles', compute="_next_cycles",
                                help="Cycles of the machine for next "
                                "operation.")
    nextdate = fields.Date('Date', help="Expected date for next operation.")
    hours_qty = fields.Float('Quantity Hours', required=False, help="Expected "
                             "time for execution the operation. hh:mm")
    alert = fields.Boolean('1st alert')
    extra_alert = fields.Boolean('2nd alert')
    check_al1 = fields.Boolean(
        '1st alert check', help="If checked the alarm will be test at the "
        "specified parameters.")
    check_al2 = fields.Boolean(
        '2nd alert check', help="If checked the alarm will be test at the "
        "specified parameters.")
    first_margin = fields.Integer(
        'First Cycle Margin', help="A negative number means that the alarm "
        "will be activated before the condition is met")
    second_margin = fields.Integer(
        'Second Cycle Margin', help="A negative number means that the alarm"
        " will be activated before the condition is met")
    margin_fre1 = fields.Integer(
        'Frequency Margin', help="A negative number means that the alarm will"
        " be activated before the compliance date")
    interval_unit1 = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                       ('mon', 'Months'), ('year', 'Years')],
                                      'Interval Unit')
    margin_fre2 = fields.Integer(
        'Frequency Margin', help="A negative number means that the alarm will "
        "be activated before the compliance date")
    interval_unit2 = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                       ('mon', 'Months'), ('year', 'Years')],
                                      'Interval Unit')
    actcycles = fields.Integer(related='machine.actcycles')
    repair_order = fields.Many2one('mrp.repair', 'Repair Order', readonly=True)

    @api.constrains('first_margin', 'second_margin')
    def _check_cycle_margins(self):
        for record in self:
            if record.first_margin and record.second_margin and(
                    record.first_margin > record.second_margin):
                raise exceptions.ValidationError(
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
                    raise exceptions.ValidationError(
                        _("First margin must be before second"))

    @api.one
    def set_alarm1(self):
        self.check_al1 = not self.check_al1

    @api.one
    def set_alarm2(self):
        self.check_al2 = not self.check_al2

    @api.one
    @api.onchange('actcycles')
    def _check_cycles_alert(self):
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
            if not ope.alert and (res1 and res1['alert'] or
                                  res2 and res2['alert']):
                ope.alert = True
            if not ope.extra_alert and (res1 and res1['extra_alert'] or
                                        res2 and res2['extra_alert']):
                ope.extra_alert = True
