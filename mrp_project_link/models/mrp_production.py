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

from openerp import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one("project.project", string="Project")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account")

    @api.one
    @api.onchange('project_id')
    def onchange_project_id(self):
        self.analytic_account_id = self.project_id.analytic_account_id

    @api.multi
    def action_in_production(self):
        task_obj = self.env['project.task']
        for record in self:
            task_domain = [('mrp_production_id', '=', record.id),
                           ('wk_order', '=', False)]
            tasks = task_obj.search(task_domain)
            if not tasks:
                if record.product_id.default_code:
                    task_name = ("%s::[%s] %s") % (
                        record.name,
                        record.product_id.default_code,
                        record.product_id.name)
                else:
                    task_name = ("%s::%s") % (
                        record.name,
                        record.product_id.name)
                task_descr = _("""
                Manufacturing Order: %s
                Product to Produce: [%s]%s
                Quantity to Produce: %s
                Bill of Material: %s
                Planned Date: %s
                """) % (record.name, record.product_id.default_code,
                        record.product_id.name, record.product_qty,
                        record.bom_id.name, record.date_planned)
                task_values = {
                    'mrp_production_id': record.id,
                    'user_id': record.user_id.id,
                    'reviewer_id': record.user_id.id,
                    'name': task_name,
                    'project_id': record.project_id.id,
                    'description': task_descr
                }
                if 'code' in task_values.keys():
                    task_values.pop('code')
                task_obj.create(task_values)
        return super(MrpProduction, self).action_in_production()

    @api.multi
    def action_confirm(self):
        procurement_obj = self.env['procurement.order']
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        result = super(MrpProduction, self).action_confirm()
        for record in self:
            if record.project_id:
                main_project = record.project_id.id
                for move in record.move_lines:
                    if mto_record in move.product_id.route_ids:
                        move.main_project_id = main_project
                        procurements = procurement_obj.search(
                            [('move_dest_id', '=', move.id)])
                        procurements.write({'main_project_id': main_project})
                        procurements.refresh()
                        procurements.set_main_project()
        return result


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
            task_descr = _("""
            Manufacturing Order: %s
            Work Order: %s
            Workcenter: %s
            Cycle: %s
            Hour: %s
            """) % (record.production_id.name, record.name,
                    record.workcenter_id.name, record.cycle, record.hour)
            task_values = {
                'mrp_production_id': record.production_id.id,
                'wk_order': record.id,
                'user_id': False,
                'reviewer_id': record.production_id.user_id.id,
                'description': task_descr,
                'project_id': record.production_id.project_id.id,
                'parent_ids': [(6, 0, production_tasks.ids)]
            }
            if record.routing_wc_line:
                count = (
                    record.routing_wc_line.op_wc_lines.filtered(
                        lambda r: r.workcenter == record.workcenter_id
                    ).op_number or record.workcenter_id.op_number)
                op_list = record.workcenter_id.operators
                for i in range(count):
                    if len(op_list) > i:
                        task_values['user_id'] = op_list[i].id
                    task_name = (_("%s:: WO%s-%s:: %s") %
                                 (record.production_id.name,
                                  str(record.sequence).zfill(3),
                                  str(i).zfill(3), record.name))
                    task_values['name'] = task_name
                    if 'code' in task_values.keys():
                        task_values.pop('code')
                    task_obj.create(task_values)
        return res


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    task_id = fields.Many2one('project.task', string="Task")
