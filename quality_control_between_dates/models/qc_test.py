# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcTestQuestion(models.Model):
    _inherit = 'qc.test.question'

    date_start = fields.Date(string='Validity start date')
    date_stop = fields.Date(string='Validity end date')

    @api.one
    @api.constrains('date_start', 'date_stop')
    def _check_interval(self):
        if (self.date_start and self.date_stop and
                self.date_start > self.date_stop):
            raise exceptions.Warning(_('Validity start date cannot be greater '
                                       'than end date.'))

    @api.one
    @api.constrains('date_start', 'date_stop', 'test')
    def _check_line_validities(self):
        domain = [('id', '!=', self.id),
                  ('name', '=', self.name),
                  ('test', '=', self.test.id)]
        if self.date_start:
            domain.append('|')
            domain.append(('date_stop', '>=', self.date_start))
            domain.append(('date_stop', '=', False))
        if self.date_stop:
            domain.append('|')
            domain.append(('date_start', '<=', self.date_stop))
            domain.append(('date_start', '=', False))
        other_lines = self.search(domain)
        if other_lines:
            raise exceptions.Warning(_('You cannot have 2 lines of the same '
                                       'question that overlap!'))
