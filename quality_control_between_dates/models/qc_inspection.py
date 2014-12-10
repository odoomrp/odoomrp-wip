# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.multi
    def _prepare_inspection_lines(self, test, force_fill=False):
        data = super(QcInspection, self)._prepare_inspection_lines(
            test, force_fill=force_fill)
        new_data = []
        question_obj = self.env['qc.test.question']
        now = fields.Date.today()
        for line_dict in data:
            test_line_id = line_dict[2].get('test_line', False)
            if test_line_id:
                question = question_obj.browse(test_line_id)
                if ((not question.date_start or
                        question.date_start <= now) and
                        (not question.date_stop or question.date_stop >= now)):
                    new_data.append(line_dict)
        return new_data
