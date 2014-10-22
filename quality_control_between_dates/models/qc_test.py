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
from openerp import models, fields, api, exceptions, _


class QcTestTemplateLine(models.Model):
    _inherit = 'qc.test.template.line'

    date_start = fields.Date(string='Validity Start Date')
    date_end = fields.Date(string='Validity End Date')

    @api.one
    @api.constrains('date_start', 'date_end')
    def _check_interval(self):
        if (self.date_start and self.date_end and
                self.date_start > self.date_end):
            raise exceptions.Warning(_('Validity start date cannot be greater '
                                       'than end date.'))

    @api.one
    @api.constrains('date_start', 'date_end', 'test_template_id')
    def _check_line_validities(self):
        domain = [('id', '!=', self.id), ('proof_id', '=', self.proof_id.id)]
        if self.date_start:
            domain.append('|')
            domain.append(('date_end', '>=', self.date_start))
            domain.append(('date_end', '=', False))
        if self.date_end:
            domain.append('|')
            domain.append(('date_start', '<=', self.date_end))
            domain.append(('date_start', '=', False))
        other_lines = self.search(domain)
        if other_lines:
            raise exceptions.Warning(_('You cannot have 2 lines of the same '
                                       'question that overlap!'))


class QcTest(models.Model):
    _inherit = 'qc.test'

    def _prepare_test_lines(self, cr, uid, test, force_fill=False,
                            context=None):
        new_data = []
        tmpl_line_obj = self.pool['qc.test.template.line']
        now = fields.Date.context_today(self)
        data = super(QcTest, self)._prepare_test_lines(
            cr, uid, test, force_fill=force_fill, context=context)
        for line_dict in data:
            tmpl_line_id = line_dict[2].get('test_template_line_id', False)
            if tmpl_line_id:
                tmpl_line = tmpl_line_obj.browse(cr, uid, tmpl_line_id,
                                                 context=context)
                if ((not tmpl_line.date_start or
                        tmpl_line.date_start <= now) and
                        (not tmpl_line.date_end or tmpl_line.date_end >= now)):
                    new_data.append(line_dict)
        return new_data
