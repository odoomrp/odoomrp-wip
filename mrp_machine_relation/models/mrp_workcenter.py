
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, fields, api


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    machine = fields.Many2one('machinery', string='Machine')

    @api.one
    @api.onchange('machine')
    def onchange_machine(self):
        if self.machine:
            today = fields.Date.context_today(self)
            user_lst = []
            for user in self.machine.users:
                if (not user.start_date or user.start_date < today) and (
                        not user.end_date or user.end_date >= today):
                    user_lst.append(user.m_user.id)
            self.operators = user_lst
