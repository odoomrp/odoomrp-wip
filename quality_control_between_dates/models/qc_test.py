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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from datetime import date


class QcTestTemplateLine(models.Model):
    _inherit = 'qc.test.template.line'

    validity_start_date = fields.Date(string='Validity Start Date',
                                      required=True)
    validity_end_date = fields.Date(string='Validity End Date')

    @api.model
    def create(self, values):
        template_obj = self.env['qc.test.template']
        test_template_id = values.get('test_template_id', False)
        proof_id = values.get('proof_id', False)
        if test_template_id:
            template = template_obj.browse(test_template_id)
            if template.test_template_line_ids:
                for line in template.test_template_line_ids:
                    if (not line.validity_end_date and
                            line.proof_id.id == proof_id):
                        raise except_orm(_('Template Test Line Error!!'),
                                         _('You must include Validity End Date'
                                           ' in the previous lines of that'
                                           ' question.'))
        return super(QcTestTemplateLine, self).create(values)


class QcTestLine(models.Model):
    _inherit = 'qc.test.line'

    @api.one
    def write(self, values):
        found = False
        if 'valid_value_ids' in values:
            found = True
        result = super(QcTestLine, self).write(values)
        if found:
            if self.test_template_line_id:
                todaydate = str(date.today())
                date_today = todaydate.replace("-", "")
                startdate = str(self.test_template_line_id.validity_start_date)
                start_date = startdate.replace("-", "")
                enddate = self.test_template_line_id.validity_end_date
                if not enddate:
                    end_date = False
                else:
                    enddate = str(enddate)
                    end_date = enddate.replace("-", "")
                if date_today < start_date:
                    self.unlink()
                    return False
                else:
                    if end_date:
                        if date_today > end_date:
                            self.unlink()
                            return False
        return result
