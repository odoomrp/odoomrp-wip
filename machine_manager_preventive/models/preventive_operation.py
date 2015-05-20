
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


class PreventiveOperationtype(models.Model):
    _name = 'preventive.operation.type'
    _description = 'Machinery preventive operation template type'

    name = fields.Char('Name')
    ref = fields.Char('Operation Reference')
    cycles = fields.Integer('Cycles')
    basedoncy = fields.Boolean('Based on Cycles')
    basedontime = fields.Boolean('Based on Time')
    margin_cy1 = fields.Integer(
        'Cycles Margin 1', help="A negative number means that the alarm will "
        "be activated before the condition is met")
    margin_cy2 = fields.Integer('Cycles Margin 2')
    frequency = fields.Integer('Frequency', help="Estimated time for the next"
                               " operation.")
    meas_unit = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                  ('mon', 'Months'), ('year', 'Years')],
                                 'Meas.')
    margin_fre1 = fields.Integer(
        'Frequency Margin 1', help="A negative number means that the alarm "
        "will be activated before the compliance date")
    meas_unit1 = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                   ('mon', 'Months'), ('year', 'Years')],
                                  'Meas.')
    margin_fre2 = fields.Integer(
        'Frequency Margin 2', help="A negative number means that the alarm "
        "will be activated before the compliance date")
    meas_unit2 = fields.Selection([('day', 'Days'), ('week', 'Weeks'),
                                   ('mon', 'Months'), ('year', 'Years')],
                                  'Meas.')
    description = fields.Text('Description')
    hours_qty = fields.Float('Quantity Hours', required=False,
                             help="Expected time for the execution of the "
                             "operation. hh:mm")

    @api.one
    @api.onchange('meas_unit')
    def onchange_meas_unit(self):
        if self.meas_unit:
            self.meas_unit1 = self.meas_unit
            self.meas_unit2 = self.meas_unit

    @api.one
    @api.onchange('margin_cy1', 'margin_cy2')
    def check_cycle_margins(self):
        if self.margin_cy1 and self.margin_cy2 and (
                self.margin_cy1 > self.margin_cy2):
            raise exceptions.Warning(_('First margin should be before second'))

    @api.one
    @api.onchange('margin_fre1', 'meas_unit1', 'margin_fre2', 'meas_unit2')
    def check_time_margins(self):
        if self.meas_unit1 and self.meas_unit2:
            margins = self._get_freq_date(self)
            if margins['first'] > margins['second']:
                raise exceptions.Warning(
                    _('First margin should be before second'))

    def _get_freq_date(self, operation):
        """ Returns Frecuency values for current operation
        @param operation: Preventive operation type to check
        @return: First and second frequency dates
        """
        frequencies = {}
        op_date = fields.Date.today()
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


class PreventiveOperationMaterial(models.Model):
    _name = "preventive.operation.material"
    _description = "New material line."

    op_machi_mat = fields.Many2one('preventive.operation.matmach', 'Operation')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_uom_qty = fields.Float('Quantity', default='1')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure',
                                  required=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id


class PreventiveOperationMatmach(models.Model):
    # operation_machine_materials
    _name = 'preventive.operation.matmach'
    _description = 'Operation - Material - Machine Relation'

    name = fields.Char('Name')
    optype_id = fields.Many2one('preventive.operation.type', 'Operation')
    opmaster = fields.Many2one('preventive.master', 'Master Operation')
    material = fields.One2many('preventive.operation.material', 'op_machi_mat',
                               'Material')
    basedoncy = fields.Boolean(related='optype_id.basedoncy')
    basedontime = fields.Boolean(related='optype_id.basedontime')
    cycles = fields.Integer(related='optype_id.cycles')
    frequency = fields.Integer(related='optype_id.frequency')
    meas_unit = fields.Selection(related='optype_id.meas_unit')
    hours_qty = fields.Float(related='optype_id.hours_qty')
    description = fields.Text('Description')

    @api.one
    @api.onchange('optype_id')
    def onchange_optype_id(self):
        if self.optype_id:
            self.description = self.optype_id.description
