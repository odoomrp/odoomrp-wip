# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class QcTestQuestion(models.Model):
    _inherit = 'qc.test.question'

    tolerance_below = fields.Float(string='Tolerance (below)', digits=(3, 2))
    tolerance_above = fields.Float(string='Tolerance (above)', digits=(3, 2))
    tolerance_percent_below = fields.Float(string='% tolerance (below)',
                                           digits=(3, 2))
    tolerance_percent_above = fields.Float(string='% tolerance (above)',
                                           digits=(3, 2))
    same_tolerance = fields.Boolean('Same tolerance above/below', default=True)

    @api.onchange('tolerance_below')
    def onchange_tolerance_below(self):
        self.tolerance_percent_below = 100 * self.min_value - self.tolerance_below / self.min_value

    @api.onchange('tolerance_percent_below')
    def onchange_tolerance_percent_below(self):
        self.tolerance_below = (
            self.tolerance_percent_below * self.min_value / 100)

    @api.onchange('tolerance_above')
    def onchange_tolerance_above(self):
        self.tolerance_percent_above = (100 * self.tolerance_above -
                                        self.max_value / self.max_value)

    @api.onchange('tolerance_percent_above')
    def onchange_tolerance_percent_above(self):
        self.tolerance_above = (self.tolerance_percent_above *
                                self.min_value / 100)
