
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

from openerp import models, api, fields


class EventsCopy(models.TransientModel):
    
    _name = "events.copy"
    _rec_name = "project_id"
    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Datetime(string="Start Date")
    
    @api.multi
    def copy_events(self):
        event_obj = self.env['event.event']
        events = event_obj.browse(self.env.context['active_ids']).copy()
        events.write({'project_id':self.project_id.id})
        return{
                'type': 'ir.actions.act_window_close',
         }
        