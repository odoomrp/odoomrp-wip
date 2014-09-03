
# -*- encoding: utf-8 -*-
##############################################################################
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
from dateutil.relativedelta import relativedelta
from datetime import datetime


class EventsDateModify(models.TransientModel):

    _name = 'events.date.modify'
    _rec_name = 'measure'
    forward = fields.Boolean(string='Forward')
    qty = fields.Integer(string='qty')
    measure = fields.Selection([('days', 'Days'), ('months', 'Months')],
                               string='Measure')

    @api.multi
    def modify_date(self):
        event_obj = self.env['event.event']
        events = event_obj.browse(self.env.context['active_ids'])
        for event in events:
            if self.measure == 'months':
                event.write({
                    'date_begin':
                        datetime.strptime(
                            event.date_begin, "%Y-%m-%d %H:%M:%S") +
                        relativedelta(months=(self.forward and -self.qty)
                                      or self.qty),
                    'date_end':
                        datetime.strptime(
                            event.date_end, "%Y-%m-%d %H:%M:%S") +
                        relativedelta(months=(self.forward and -self.qty)
                                      or self.qty)})
            else:
                event.write({
                    'date_begin': datetime.strptime(
                        event.date_begin, "%Y-%m-%d %H:%M:%S") + relativedelta(
                            days=(self.forward and -self.qty) or self.qty),
                    'date_end':
                        datetime.strptime(event.date_end,
                                          "%Y-%m-%d %H:%M:%S") +
                        relativedelta(days=(self.forward and -self.qty)
                                      or self.qty)})
        return {'type': 'ir.actions.act_window_close'}
