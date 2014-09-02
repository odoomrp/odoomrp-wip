
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


class ProjectPartnerToEvents(models.TransientModel):

    _name = 'project.partner.to.events'

    @api.multi
    def assign_partners(self):
        registry_obj = self.env['event.registration']
        event_obj = self.env['event.event']
        for event in event_obj.browse(event_obj.env.context['active_ids']):
            for partner in event.project_id.partner_lines:
                if not registry_obj.search_count(
                        [('event_id', '=', event.id),
                         ('partner_id', '=', partner.id)]):
                    registry = registry_obj.create({
                        'partner_id': partner.id,
                        'event_id': event.id,
                        'name': partner.name,
                        'email': partner.email,
                        'phone': partner.phone,
                        'message_follower_ids': [
                            (4, partner.id),
                            (4, event.user_id.partner_id.id)]})
        return{'type': 'ir.actions.act_window_close'}
