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

from openerp import models, api


class CreateProjectMrp(models.TransientModel):

    _name = 'create.project.mrp.wiz'

    @api.multi
    def create_project(self):
        mrp_production_obj = self.env['mrp.production']
        project_obj = self.env['project.project']
        ctx = self.env.context
        if 'active_id' in ctx:
            production = mrp_production_obj.browse(ctx.get('active_id'))
            if not production.project_id:
                project_lst = project_obj.search([('name', '=',
                                                   production.name)], limit=1)
                if project_lst:
                    project = project_lst
                else:
                    project_vals = {'name': production.name,
                                    'use_tasks': True,
                                    'use_timesheets': True,
                                    'use_issues': True
                                    }
                    project = project_obj.create(project_vals)
                production.project_id = project.id
                production.analytic_account_id = project.analytic_account_id.id
            production.signal_workflow('button_confirm')
        return {'type': 'ir.actions.act_window_close'}
