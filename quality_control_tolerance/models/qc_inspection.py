# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    @api.one
    @api.depends('question_type', 'test_line', 'min_value',
                 'max_value', 'test_line.percen_permissible_tolerance')
    def _compute_min_max_allowed_variable(self):
        self.min_allowed = 0.0
        self.max_allowed = 0.0
        self.min_variable = 0.0
        self.max_variable = 0.0
        if self.question_type != 'qualitative' and self.test_line:
            perm = self.test_line.percen_permissible_tolerance
            var = self.test_line.percen_variable_tolerance
            if self.min_value:
                if perm:
                    self.min_allowed = (
                        self.min_value - self.min_value * perm / 100)
                if var:
                    self.min_variable = (
                        self.min_value - self.min_value * var / 100)
            if self.max_value:
                if perm:
                    self.max_allowed = (
                        self.max_value + self.max_value * perm / 100)
                if var:
                    self.max_variable = (
                        self.max_value + self.max_value * var / 100)

    @api.one
    @api.depends('test.state', 'min_value', 'max_value', 'min_allowed',
                 'max_allowed', 'min_variable', 'max_variable',
                 'quantitative_value', 'uom_id', 'test_uom_id')
    def _compute_tolerance_status(self):
        self.tolerance_status = 'noadmissible'
        self.success = False
        if self.question_type != 'qualitative' and self.test_line:
            amount = self.quantitative_value
            if self.min_value <= amount <= self.max_value:
                self.success = True
                self.tolerance_status = 'optimal'
            elif (self.min_allowed and self.min_variable and
                  self.max_allowed and self.max_variable):
                if ((self.min_variable <= amount < self.min_allowed) or
                        (self.max_allowed <= amount <= self.max_variable)):
                    self.tolerance_status = 'admissible'
                elif ((self.min_variable <= amount < self.min_value) or
                        (self.max_value < amount < self.max_variable)):
                    self.tolerance_status = 'tolerable'
            elif self.min_allowed and self.max_allowed:
                if ((self.min_allowed <= amount < self.min_value) or
                        (self.max_value <= amount <= self.max_allowed)):
                    self.tolerance_status = 'admissible'
            elif self.min_variable and self.max_variable:
                if ((self.min_variable <= amount < self.min_value) or
                        (self.max_value < amount < self.max_variable)):
                    self.tolerance_status = 'tolerable'
        elif self.question_type == 'qualitative' and self.test_line:
            for valid_value in self.possible_ql_values:
                if (self.qualitative_value.id == valid_value.id and
                        valid_value.ok):
                    self.tolerance_status = 'optimal'
                    break

    tolerance_status = fields.Selection(
        [('optimal', 'Optimal'),
         ('tolerable', 'Tolerable'),
         ('admissible', 'Admissible'),
         ('noadmissible', 'Not admissible')],
        string='Tolerance Status', compute='_compute_tolerance_status')
    min_allowed = fields.Float(string='Minimum allowed', digits=(5, 2),
                               compute='_compute_min_max_allowed_variable')
    max_allowed = fields.Float(string='Maximum allowed', digits=(5, 2),
                               compute='_compute_min_max_allowed_variable')
    min_variable = fields.Float(string='Minimum variable', digits=(5, 2),
                                compute='_compute_min_max_allowed_variable')
    max_variable = fields.Float(string='Maximum variable', digits=(5, 2),
                                compute='_compute_min_max_allowed_variable')

