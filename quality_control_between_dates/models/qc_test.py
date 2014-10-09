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
from datetime import date


class QcTestTemplateLine(models.Model):
    _inherit = 'qc.test.template.line'

    validity_start_date = fields.Date(string='Validity Start Date',
                                      required=True)
    validity_end_date = fields.Date(string='Validity End Date')

    @api.one
    @api.constrains('validity_start_date', 'validity_end_date',
                    'test_template_id')
    def _check_validity_end_date(self):
        start_date = self.validity_start_date
        end_date = self.validity_end_date
        if not self.validity_end_date and self.test_template_id:
            if self.test_template_id.test_template_line_ids:
                for line in self.test_template_id.test_template_line_ids:
                    if (line.id != self.id and not line.validity_end_date and
                            line.proof_id.id == self.proof_id.id):
                        raise exceptions.Warning(_('You must include Validity'
                                                   'End Date in the previous'
                                                   ' lines of that question.'))
                    if line.validity_end_date:
                        if (line.id != self.id and
                            line.proof_id.id == self.proof_id.id and
                            start_date >= line.validity_start_date and
                                start_date <= line.validity_end_date):
                            raise exceptions.Warning(_('You must review date'
                                                       ' ranges, validity'
                                                       ' start date Error.'))
                    else:
                        if (line.id != self.id and
                            line.proof_id.id == self.proof_id.id and
                                start_date >= line.validity_start_date):
                            raise exceptions.Warning(_('You must review date'
                                                       ' ranges, validity'
                                                       ' start date Error.'))
        else:
            if start_date and self.test_template_id:
                if self.test_template_id.test_template_line_ids:
                    for line in self.test_template_id.test_template_line_ids:
                        if line.validity_end_date:
                            if (line.id != self.id and
                                line.proof_id.id == self.proof_id.id and
                                start_date >= line.validity_start_date and
                                    start_date <= line.validity_end_date):
                                raise exceptions.Warning(_('You must review'
                                                           ' date ranges,'
                                                           ' validity start'
                                                           ' date Error.'))
                        else:
                            if (line.id != self.id and
                                line.proof_id.id == self.proof_id.id and
                                    start_date >= line.validity_start_date):
                                raise exceptions.Warning(_('You must review'
                                                           ' date ranges,'
                                                           ' validity start'
                                                           ' date Error.'))
            if end_date and self.test_template_id:
                if self.test_template_id.test_template_line_ids:
                    for line in self.test_template_id.test_template_line_ids:
                        if line.validity_end_date:
                            if (line.id != self.id and
                                line.proof_id.id == self.proof_id.id and
                                end_date >= line.validity_start_date and
                                    end_date <= line.validity_end_date):
                                raise exceptions.Warning(_('You must review'
                                                           ' date ranges,'
                                                           ' validity start'
                                                           ' date Error.'))
                        else:
                            if (line.id != self.id and
                                line.proof_id.id == self.proof_id.id and
                                    end_date >= line.validity_start_date):
                                raise exceptions.Warning(_('You must review'
                                                           ' date ranges,'
                                                           ' validity start'
                                                           ' date Error.'))


class QcTest(models.Model):
    _inherit = 'qc.test'

    def _prepare_test_lines(self, cr, uid, test, force_fill=False,
                            context=None):
        templine_obj = self.pool['qc.test.template.line']
        new_data = super(QcTest, self)._prepare_test_lines(
            cr, uid, test, force_fill=force_fill, context=context)
        if new_data:
            for line in new_data:
                test_line = line[2]
                templine_id = test_line.get('test_template_line_id', False)
                if templine_id:
                    templine = templine_obj.browse(cr, uid, templine_id,
                                                   context)
                    start_date = fields.Date.from_string(
                        templine.validity_start_date)
                    if not templine.validity_end_date:
                        end_date = False
                    else:
                        end_date = fields.Date.from_string(
                            templine.validity_end_date)
                    if date.today() < start_date:
                        id = new_data.index(line)
                        new_data.pop(id)
                    else:
                        if end_date:
                            if date.today() > end_date:
                                id = new_data.index(line)
                                new_data.pop(id)
        return new_data
