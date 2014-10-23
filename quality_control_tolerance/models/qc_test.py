# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api


class QcTest(models.Model):
    _inherit = 'qc.test'


class QcTestTemplateLine(models.Model):
    _inherit = 'qc.test.template.line'

    percen_permissible_tolerance = fields.Float(
        string='% Optimal allowed tolerance', digits=(3, 2))
    percen_variable_tolerance = fields.Float(
        string='% Variable tolerance', digits=(3, 2))


class QcTestLine(models.Model):
    _inherit = 'qc.test.line'

    @api.one
    @api.depends('proof_type', 'test_template_line_id', 'min_value',
                 'test_template_line_id.percen_permissible_tolerance')
    def _compute_min_allowed(self):
        self.min_allowed = 0.0
        if (self.proof_type != 'qualitative' and self.test_template_line_id
                and self.min_value):
            per = self.test_template_line_id.percen_permissible_tolerance
            if per:
                self.min_allowed = (self.min_value - self.min_value * per /
                                    100)

    @api.one
    @api.depends('proof_type', 'test_template_line_id', 'max_value',
                 'test_template_line_id.percen_permissible_tolerance')
    def _compute_max_allowed(self):
        self.max_allowed = 0.0
        if (self.proof_type != 'qualitative' and self.test_template_line_id and
                self.max_value):
            per = self.test_template_line_id.percen_permissible_tolerance
            if per:
                self.max_allowed = (self.max_value + self.max_value * per /
                                    100)

    @api.one
    @api.depends('proof_type', 'test_template_line_id', 'min_value',
                 'test_template_line_id.percen_variable_tolerance')
    def _compute_min_variable(self):
        self.min_variable = 0.0
        if (self.proof_type != 'qualitative' and self.test_template_line_id and
                self.min_value):
            per = self.test_template_line_id.percen_variable_tolerance
            if per:
                self.min_variable = (self.min_value - self.min_value * per
                                     / 100)

    @api.one
    @api.depends('proof_type', 'test_template_line_id', 'max_value',
                 'test_template_line_id.percen_variable_tolerance')
    def _compute_max_variable(self):
        self.max_variable = 0.0
        if (self.proof_type != 'qualitative' and self.test_template_line_id and
                self.max_value):
            per = self.test_template_line_id.percen_variable_tolerance
            if per:
                self.max_variable = (self.max_value + self.max_value * per
                                     / 100)

    @api.one
    @api.depends('test_id.state', 'min_value', 'max_value', 'min_allowed',
                 'max_allowed', 'min_variable', 'max_variable',
                 'actual_value_qt', 'uom_id', 'test_uom_id')
    def _compute_tolerance_status(self):
        uom_obj = self.pool['product.uom']
        self.tolerance_status = 'noadmissible'
        self.success = False
        if (self.proof_type != 'qualitative' and self.test_template_line_id):
            amount = uom_obj._compute_qty(
                self._cr, self._uid, self.uom_id.id, self.actual_value_qt,
                self.test_uom_id.id)
            if self.min_value <= amount <= self.max_value:
                self.success = True
                self.tolerance_status = 'optimal'
            elif ((self.min_allowed <= amount < self.min_variable)
                  or (self.max_variable <= amount <= self.max_allowed)):
                self.tolerance_status = 'tolerable'
                self.success = True
            elif ((self.min_variable <= amount < self.min_value) or
                  (self.max_value < amount < self.max_variable)):
                self.tolerance_status = 'admissible'
                self.success = True

    tolerance_status = fields.Selection(
        [('optimal', 'Optimal'),
         ('tolerable', 'Tolerable'),
         ('admissible', 'Admissible'),
         ('noadmissible', 'Not Admissible'),
         ], string='Tolerance Status', compute='_compute_tolerance_status')
    min_allowed = fields.Float(string='Minimum allowed', digits=(5, 2),
                               compute='_compute_min_allowed')
    max_allowed = fields.Float(string='Maximum allowed', digits=(5, 2),
                               compute='_compute_max_allowed')
    min_variable = fields.Float(string='Minimum variable', digits=(5, 2),
                                compute='_compute_min_variable')
    max_variable = fields.Float(string='Maximum variable', digits=(5, 2),
                                compute='_compute_max_variable')
