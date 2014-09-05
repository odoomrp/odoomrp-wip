
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2013 AvanzOSC S.L. (Mikel Arregi) All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import api, models, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class OperationTime(models.Model):

    _inherit = 'mrp.production.workcenter.line'
    operation_time_lines = fields.One2many('operation.time.lines',
                                           'operation_time')


class OperationTimeLines(models.Model):

    _name = 'operation.time.lines'
    _rec_name = 'operation_time'
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    operation_time = fields.Many2one('mrp.production.workcenter.line')
    uptime = fields.Float(string='Uptime', compute='operation_uptime',
                          store=True, digits=(12, 6))
    production = fields.Many2one('mrp.production',
                                 related='operation_time.production_id',
                                 string='Production', store=True)

    @api.one
    @api.depends('start_date', 'end_date')
    def operation_uptime(self):
        if self.end_date and self.start_date:
            timedelta = datetime.strptime(self.end_date,
                                          DEFAULT_SERVER_DATETIME_FORMAT) - \
                datetime.strptime(self.start_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT)
            self.uptime = timedelta.total_seconds()/3600.
        else:
            self.uptime = 0
        return True
