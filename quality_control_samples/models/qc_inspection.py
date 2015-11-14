# -*- coding: utf-8 -*-
# (c) 2014-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.multi
    def _prepare_inspection_lines(self, test, force_fill=False):
        res = super(QcInspection, self)._prepare_inspection_lines(
            test, force_fill=force_fill)
        if test.sample:
            num_samples = test.sample.get_samples_number(self[:1].qty or 1.0)
            if num_samples:
                new_data = []
                for i in range(num_samples):
                    for line_tuple in res:
                        line = line_tuple[2].copy()
                        line['sample_number'] = i + 1
                        new_data.append((0, 0, line))
                return new_data
        return res


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'
    _order = 'sample_number, id'

    sample_number = fields.Integer(string='# sample', readonly=True, default=1)
