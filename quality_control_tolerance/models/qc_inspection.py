# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, _


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    @api.multi
    def _prepare_inspection_line(self, test, line, fill=None):
        res = super(QcInspection, self)._prepare_inspection_line(
            test, line, fill=fill)
        res['min_value_below'] = line.min_value_below
        res['max_value_above'] = line.max_value_above
        return res


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    @api.one
    @api.depends('quantitative_value', 'min_value', 'max_value',
                 'test_uom_id', 'min_value_below', 'max_value_above',
                 'question_type', 'uom_id')
    def _compute_tolerance_status(self):
        self.tolerance_status = 'not_tolerable'
        if self.question_type == 'quantitative':
            if self.uom_id.id == self.test_uom_id.id:
                amount = self.quantitative_value
            else:
                amount = self.env['product.uom']._compute_qty(
                    self.uom_id.id, self.quantitative_value,
                    self.test_uom_id.id)
            if amount >= self.min_value_below:
                if amount >= self.min_value:
                    if amount <= self.max_value:
                        self.tolerance_status = 'optimal'
                    elif amount <= self.max_value_above:
                        self.tolerance_status = 'tolerable'
                else:
                    self.tolerance_status = 'tolerable'
        elif self.question_type == 'qualitative':
            self.tolerance_status = self.qualitative_value.tolerance_status

    @api.one
    @api.depends('possible_ql_values', 'min_value', 'max_value', 'test_uom_id',
                 'question_type', 'min_value_below', 'max_value_above')
    def get_valid_values(self):
        if self.question_type == 'qualitative':
            super(QcInspectionLine, self).get_valid_values()
            self.valid_values = ", ".join([x.name for x in
                                           self.possible_ql_values if x.ok])
            self.valid_values += ", " + ", ".join(
                [_("%s (tolerable)") % x.name for x in self.possible_ql_values
                 if not x.ok and x.tolerance_status == 'tolerable'])
        elif self.question_type == 'quantitative':
            self.valid_values = "(%s) %s-%s (%s)" % (
                self.min_value_below, self.min_value, self.max_value,
                self.max_value_above)
            if self.env.ref("product.group_uom") in self.env.user.groups_id:
                self.valid_values += " %s" % self.test_uom_id.name

    tolerance_status = fields.Selection(
        [('optimal', 'Optimal'),
         ('tolerable', 'Tolerable'),
         ('not_tolerable', 'Not tolerable')],
        string='Tolerance status', compute='_compute_tolerance_status')
    min_value_below = fields.Float(string='Min. tolerable')
    max_value_above = fields.Float(string='Max. tolerable')
