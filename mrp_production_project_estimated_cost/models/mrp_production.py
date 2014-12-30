# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.model
    def action_confirm(self):
        analytic_line_obj = self.env['account.analytic.line']
        res = super(MrpProduction, self).action_confirm()
        if self.state == 'draft':
            return res
        journal = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_materials',
            False)
        for line in self.product_lines:
            name = _('%s-%s' % (self.name, line.work_order.name or ''))
            vals = self._catch_information_estimated_cost(
                journal, name, self, line.work_order, line.product_id,
                line.product_qty)
            analytic_line_obj.create(vals)
        journal = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_machines',
            False)
        for line in self.workcenter_lines:
            workcenter = line.workcenter_id
            if (workcenter.time_start and
                    workcenter.pre_op_product):
                name = (_('%s-%s Pre-operation') %
                        (self.name, workcenter.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    workcenter.pre_op_product,
                    workcenter.time_start)
                vals.update({'amount':
                             workcenter.pre_op_product.standard_price})
                analytic_line_obj.create(vals)
            if (workcenter.time_stop and
                    workcenter.post_op_product):
                name = (_('%s-%s Post-operation') %
                        (self.name, workcenter.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    workcenter.post_op_product,
                    workcenter.time_stop)
                vals.update({'amount':
                             workcenter.post_op_product.standard_price})
                analytic_line_obj.create(vals)
            if line.cycle and workcenter.product_id:
                name = (_('%s-%s-C-%s') %
                        (self.name, line.routing_wc_line.operation.code,
                         workcenter.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    workcenter.product_id, line.cycle)
                analytic_line_obj.create(vals)
            if line.hour and workcenter.product_id:
                name = (_('%s-%s-H-%s') %
                        (self.name, line.routing_wc_line.operation.code,
                         workcenter.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    workcenter.product_id, line.hour)
                analytic_line_obj.create(vals)
            for op_wc_line in line.routing_wc_line.op_wc_lines:
                if (op_wc_line.workcenter.id ==
                    workcenter.id and
                    workcenter.product_id and
                        op_wc_line.op_number > 0):
                    journal = self.env.ref(
                        'mrp_production_project_estimated_cost.analytic_'
                        'journal_operators', False)
                    name = (_('%s-%s-%s') %
                            (self.name, line.routing_wc_line.operation.code,
                             workcenter.product_id.name))
                    vals = self._catch_information_estimated_cost(
                        journal, name, self, line,
                        workcenter.product_id, op_wc_line.op_number)
                    analytic_line_obj.create(vals)
        return res

    def _catch_information_estimated_cost(self, journal, name, production,
                                          workorder, product, qty):
        analytic_line_obj = self.env['account.analytic.line']
        general_account = (product.property_account_income or
                           product.categ_id.property_account_income_categ
                           or False)
        if not general_account:
            raise exceptions.Warning(
                _('You must define Income account in the product "%s", or in'
                  ' the product category') % (product.name))
        if not self.analytic_account_id:
            raise exceptions.Warning(
                _('You must define one Analytic Account for this MO'))
        vals = {
            'name': name,
            'mrp_production_id': production.id,
            'workorder': workorder.id,
            'account_id': self.analytic_account_id.id,
            'journal_id': journal.id,
            'user_id': self._uid,
            'date': analytic_line_obj._get_default_date(),
            'product_id': product.id,
            'unit_amount': qty,
            'product_uom_id': product.uom_id.id,
            'general_account_id': general_account.id,
            'estim_standard_cost': qty * product.manual_standard_cost,
            'estim_average_cost': qty * product.standard_price,
        }
        return vals
