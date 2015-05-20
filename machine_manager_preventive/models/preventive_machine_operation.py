
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

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
    meas_unit = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                  ('mon', 'Months'), ('year', 'Years')],
                                 'Meas.')
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
    meas_unit1 = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                   ('mon', 'Months'), ('year', 'Years')],
                                  'Meas.')
    margin_fre2 = fields.Integer(
        'Frequency Margin', help="A negative number means that the alarm will "
        "be activated before the compliance date")
    meas_unit2 = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                   ('mon', 'Months'), ('year', 'Years')],
                                  'Meas.')
    actcycles = fields.Integer(related='machine.actcycles')
    repair_order = fields.Many2one('mrp.repair', 'Repair Order', readonly=True)

    @api.one
    @api.onchange('first_margin', 'second_margin')
    def check_cycle_margins(self):
        if self.first_margin and self.second_margin and (
                self.first_margin > self.second_margin):
            raise exceptions.Warning(_('First margin should be before second'))

    @api.one
    @api.onchange('margin_fre1', 'meas_unit1', 'margin_fre2', 'meas_unit2')
    def check_time_margins(self):
        if self.meas_unit1 and self.meas_unit2:
            margins = self._get_freq_date(self)
            if margins['first'] > margins['second']:
                raise exceptions.Warning(
                    _('First margin should be before second'))

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
        frequencies = self._get_freq_date(operation)
        date = fields.Date.today()
        if 'first' in frequencies:
            freq1 = frequencies['first']
        if 'second' in frequencies:
            freq2 = frequencies['second']
        res = {'alert': False, 'extra_alert': False}
        if (date >= freq1 and operation.check_al1):
            res['alert'] = True
        if (date >= freq2 and operation.check_al2):
            res['extra_alert'] = True
        return res

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
    def _alert_create(self):
        ids = self.search([])
        for ope in ids:  # Loop for all operations
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

    def _get_freq_date(self, operation):
        """ Returns Frecuency values for current operation
        @param operation: Preventive operation for machine to check
        @return: First and second frequency dates
        """
        frequencies = {}
        date = fields.Date.today()
        op_date = (operation.nextdate or operation.lastdate or
                   operation.machine.enrolldate or date)
        if operation.meas_unit1:
            if operation.meas_unit1 == 'day':
                freq1 = fields.Date.from_string(op_date) + (
                    relativedelta(days=operation.margin_fre1))
            elif operation.meas_unit1 == 'week':
                freq1 = fields.Date.from_string(op_date) + (
                    relativedelta(weeks=operation.margin_fre1))
            elif operation.meas_unit1 == 'mon':
                freq1 = fields.Date.from_string(op_date) + (
                    relativedelta(months=operation.margin_fre1))
            else:
                freq1 = fields.Date.from_string(op_date) + (
                    relativedelta(years=operation.margin_fre1))
            frequencies['first'] = fields.Date.to_string(freq1)
        if operation.meas_unit2:
            if operation.meas_unit2 == 'day':
                freq2 = fields.Date.from_string(op_date) + (
                    relativedelta(days=operation.margin_fre2))
            elif operation.meas_unit2 == 'week':
                freq2 = fields.Date.from_string(op_date) + (
                    relativedelta(weeks=operation.margin_fre2))
            elif operation.meas_unit2 == 'mon':
                freq2 = fields.Date.from_string(op_date) + (
                    relativedelta(months=operation.margin_fre2))
            else:
                freq2 = fields.Date.from_string(op_date) + (
                    relativedelta(years=operation.margin_fre2))
            frequencies['second'] = fields.Date.to_string(freq2)
        return frequencies

    @api.multi
    def update_alerts(self, operation):
        if operation.cycles > 0:
            operation.lastcycles = operation.actcycles
            self._check_alert_by_cycles(operation)
        if operation.frequency > 0:
            op_freq = operation.frequency
            op_meas = operation.meas_unit
            operation.lastdate = fields.Date.today()
            time_now = fields.Date.from_string(fields.Date.today())
            if op_meas == 'day':
                calc_date = time_now + relativedelta(days=op_freq)
            elif op_meas == 'week':
                calc_date = time_now + relativedelta(weeks=op_freq)
            elif op_meas == 'mon':
                calc_date = time_now + relativedelta(months=op_freq)
            else:
                calc_date = time_now + relativedelta(years=op_freq)
            operation.nextdate = calc_date
            self._check_alert_by_time(operation)

    @api.one
    def set_alarm1(self):
        self.check_al1 = not self.check_al1

    @api.one
    def set_alarm2(self):
        self.check_al2 = not self.check_al2
