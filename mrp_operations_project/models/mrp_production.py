# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, _


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.model
    def _prepare_tasks_vals(self, workorder, task_vals):
        tasks_vals = []
        wk_operation = workorder.routing_wc_line.op_wc_lines.filtered(
            lambda r: r.workcenter == workorder.workcenter_id)[:1]
        count = (wk_operation.op_number or
                 workorder.workcenter_id.op_number)
        op_list = workorder.workcenter_id.operators
        for i in range(count):
            # Create a task for each employee
            if len(op_list) > i:
                task_vals['user_id'] = op_list[i].id
            task_name = (_("%s:: WO%s-%s:: %s") %
                         (workorder.production_id.name,
                          str(workorder.sequence).zfill(3),
                          str(i).zfill(3), workorder.name))
            task_vals['name'] = task_name
            tasks_vals.append(task_vals)
        return tasks_vals
