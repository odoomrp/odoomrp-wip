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


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    analytic_account_id = fields.Many2one("account.analytic.account",
                                          string="Analytic Account")
    project_id = fields.Many2one("project.project", string="Project")

    @api.multi
    def action_in_production(self):
        task_obj = self.env['project.task']
        project_obj = self.env['project.project']
        for record in self:
            project_id = False
            if record.project_id:
                project_id = record.project_id
            else:
                project_domain = [('analytic_account_id', '=',
                                   record.analytic_account_id.id)]
                projects = project_obj.search(project_domain)
                
                if projects:
                    project_id = projects[0]
                else:
                    analytic_account = record.analytic_account_id.id
                    proj_vals = {'use_tasks': True,
                                 'analytic_account_id': analytic_account,
                                 'user_id': record.user_id.id,
                                }
                    project_id = project_obj.create(proj_vals)
                record.project_id = project_id.id
            task_domain = [('mrp_production_id', '=', record.id),
                           ('wk_order', '=', False)]
            tasks = task_obj.search(task_domain)
            if not tasks:
                task_name = ("%s:: [%s]%s") % (record.name,
                                               record.product_id.default_code,
                                               record.product_id.name)
                task_descr = ("""
                Manufacturing Order: %s
                Product to Produce: [%s]%s
                Quantity to Produce: %s
                Bill of Material: %s
                Planned Date: %s
                """) % (record.name, record.product_id.default_code,
                        record.product_id.name, record.product_qty,
                        record.bom_id.name, record.date_planned)
                task_values = {'mrp_production_id': record.id,
                               'user_id': record.user_id.id,
                               'reviewer_id': record.user_id.id,
                               'name': task_name,
                               'project_id': project_id.id,
                               'description': task_descr
                               }
                task_obj.create(task_values)
        res = super(MrpProduction, self).action_in_production()
        return res


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    def action_start_working(self):
        task_obj = self.env['project.task']
        res = super(MrpProductionWorkcenterLine, self).action_start_working()
        for record in self:
            task_domain = [('mrp_production_id', '=', record.production_id.id),
                           ('wk_order', '=', False)]
            production_tasks = task_obj.search(task_domain)
            task_descr = ("""
            Manufacturing Order: %s
            Work Order: %s
            Workcenter: %s
            Cycle: %s
            Hour: %s
            """) % (record.production_id.name, record.name,
                    record.workcenter_id.name, record.cycle, record.hour)
            task_values = {'mrp_production_id': record.production_id.id,
                           'wk_order': record.id,
                           'user_id': False,
                           'reviewer_id': record.production_id.user_id.id,
                           'description': task_descr,
                           'project_id': record.production_id.project_id.id,
                           'parent_ids': [(6, 0, production_tasks.ids)]
                           }
            if record.routing_wc_line.operation:
                count = record.routing_wc_line.operation.op_number
                if count > 0:
                    while count > 0:
                        task_name = ("%s:: WO%s-%s:: %s") % \
                                    (record.production_id.name,
                                     str(record.sequence).zfill(3),
                                     str(count).zfill(3), record.name)
                        task_values['name'] = task_name
                        task_obj.create(task_values)
                        count -= 1
        return res
