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
from datetime import datetime


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def action_production_end(self):
        analytic_line_obj = self.env['account.analytic.line']
        for record in self:
            analytic_lines = analytic_line_obj.search([('mrp_production_id',
                                                        '=', record.id)])
            production_total_cost = 0.0
            for line in analytic_lines:
                production_total_cost += abs(line.amount)
            product = record.product_id
            if product.cost_method == 'average':
                new_product_qty = record.product_qty
                old_product_qty = (product.qty_available - new_product_qty)
                old_product_cost = product.standard_price
                new_product_cost = (old_product_qty * old_product_cost +
                                    production_total_cost) / (old_product_qty +
                                                              new_product_qty)
                product.standard_price = new_product_cost
        return super(MrpProduction, self).action_production_end()


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    def _create_analytic_line(self):
        analytic_line_obj = self.env['account.analytic.line']
        task_obj = self.env['project.task']
        hour_uom = self.env.ref('product.product_uom_hour', False)
        operation_line = self.operation_time_lines[-1]
        quantity = operation_line.uptime
        production = self.production_id
        workcenter = self.workcenter_id
        product = workcenter.product_id
        journal_id = workcenter.costs_journal_id.id or False
        analytic_account_id = production.analytic_account_id.id or False
        task_id = False
        if production:
            task = task_obj.search([('mrp_production_id', '=', production.id),
                                    ('wk_order', '=', False)])
            if task:
                task_id = task[0].id
        name = ((production.name or '') + '-' +
                (self.routing_wc_line.operation.code or '') + '-' +
                (product.default_code or ''))
        general_account = workcenter.costs_general_account_id.id or False
        price = workcenter.costs_hour
        if price > 0.0:
            analytic_vals = {'name': name,
                             'ref': name,
                             'date': datetime.now().strftime('%Y-%m-%d'),
                             'user_id': self.env.uid,
                             'product_id': product.id,
                             'product_uom_id': hour_uom.id,
                             'amount': -(price * quantity),
                             'unit_amount': quantity,
                             'journal_id': journal_id,
                             'account_id': analytic_account_id,
                             'general_account_id': general_account,
                             'task_id': task_id,
                             'mrp_production_id': production.id or False,
                             'workorder': self.id,
                             }
            analytic_line = analytic_line_obj.create(analytic_vals)
            return analytic_line

    def action_pause(self):
        result = super(MrpProductionWorkcenterLine, self).action_pause()
        self._create_analytic_line()
        return result

    def action_done(self):
        result = super(MrpProductionWorkcenterLine, self).action_done()
        self._create_analytic_line()
        return result
