# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class QcTestQuestion(models.Model):
    _inherit = 'qc.test.question'

    tolerance_below = fields.Float(string='Tolerance (below)')
    tolerance_above = fields.Float(string='Tolerance (above)')
    tolerance_percent_below = fields.Float(string='% tolerance (below)',
                                           digits=(3, 2))
    tolerance_percent_above = fields.Float(string='% tolerance (above)',
                                           digits=(3, 2))
    same_tolerance = fields.Boolean('Same tolerance above/below', default=True)

    @api.one
    @api.onchange('min_value', 'max_value')
    def onchange_values(self):
        self.onchange_tolerance_below()
        self.onchange_tolerance_above()

    @api.one
    @api.onchange('same_tolerance')
    def onchange_same_tolerance(self):
        self.tolerance_percent_above = self.tolerance_percent_below
        self.tolerance_above = self.tolerance_below

    @api.one
    @api.onchange('tolerance_below')
    def onchange_tolerance_below(self):
        diff = self.max_value - self.min_value
        self.tolerance_percent_below = 100 * self.tolerance_below / diff
        if self.same_tolerance:
            self.onchange_same_tolerance()

    @api.one
    @api.onchange('tolerance_percent_below')
    def onchange_tolerance_percent_below(self):
        diff = self.max_value - self.min_value
        self.tolerance_below = self.tolerance_percent_below * diff / 100
        if self.same_tolerance:
            self.onchange_same_tolerance()

    @api.one
    @api.onchange('tolerance_above')
    def onchange_tolerance_above(self):
        diff = self.max_value - self.min_value
        self.tolerance_percent_above = 100 * self.tolerance_above / diff

    @api.one
    @api.onchange('tolerance_percent_above')
    def onchange_tolerance_percent_above(self):
        diff = self.max_value - self.min_value
        self.tolerance_above = self.tolerance_percent_above * diff / 100


class QcTestQuestionValue(models.Model):
    _inherit = 'qc.test.question.value'

    @api.one
    @api.onchange('ok')
    def onchange_ok(self):
        self.tolerance_status = 'optimal' if self.ok else 'not_tolerable'

    tolerance_status = fields.Selection(
        [('optimal', 'Optimal'),
         ('tolerable', 'Tolerable'),
         ('not_tolerable', 'Not tolerable')],
        string='Tolerance status', default='not_tolerable')
