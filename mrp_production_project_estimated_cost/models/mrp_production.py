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
from openerp import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    active = fields.Boolean('Active', default=False)
    name = fields.Char(
        string='Referencen', required=True, readonly=True, copy="False",
        states={'draft': [('readonly', False)]}, default="/")

    @api.model
    def create(self, values):
        sequence_obj = self.pool['ir.sequence']
        if values['active']:
            values['name'] = sequence_obj.get(self._cr, self._uid,
                                              'mrp.production')
        else:
            values['name'] = sequence_obj.get(self._cr, self._uid,
                                              'fictitious.mrp.production')
        return super(MrpProduction, self).create(values)

    @api.multi
    def unlink(self):
        analytic_line_obj = self.env['account.analytic.line']
        for production in self:
            cond = [('mrp_production_id', '=', self.id)]
            analytic_line_obj.search(cond).unlink()
        return super(MrpProduction, self).unlink()

    @api.multi
    def action_compute(self, properties=None):
        self.ensure_one()
        res = super(MrpProduction, self).action_compute(properties=properties)
        self._calculate_production_estimated_cost()
        return res

    def _calculate_production_estimated_cost(self):
        analytic_line_obj = self.env['account.analytic.line']
        cond = [('mrp_production_id', '=', self.id)]
        analytic_line_obj.search(cond).unlink()
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
            for op_workcenter in line.routing_wc_line.op_wc_lines:
                if line.workcenter_id == op_workcenter.workcenter:
                    workcenter = op_workcenter
                    break
            time_start = workcenter.time_start
            time_stop = workcenter.time_stop
            op_number = workcenter.op_number
            op_avg_cost = workcenter.op_avg_cost
            if (time_start and line.workcenter_id.pre_op_product):
                name = (_('%s-%s Pre-operation') %
                        (self.name, line.workcenter_id.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    line.workcenter_id.pre_op_product, time_start)
                vals.update({'amount':
                             line.workcenter_id.pre_op_product.standard_price})
                analytic_line_obj.create(vals)
            if (time_stop and line.workcenter_id.post_op_product):
                name = (_('%s-%s Post-operation') %
                        (self.name, line.workcenter_id.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    line.workcenter_id.post_op_product, time_stop)
                vals.update(
                    {'amount':
                     line.workcenter_id.post_op_product.standard_price})
                analytic_line_obj.create(vals)
            if line.cycle and line.workcenter_id.product_id:
                name = (_('%s-%s-C-%s') %
                        (self.name, line.routing_wc_line.operation.code,
                         line.workcenter_id.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    line.workcenter_id.product_id, line.cycle)
                analytic_line_obj.create(vals)
            if line.hour and line.workcenter_id.product_id:
                name = (_('%s-%s-H-%s') %
                        (self.name, line.routing_wc_line.operation.code,
                         line.workcenter_id.name))
                vals = self._catch_information_estimated_cost(
                    journal, name, self, line,
                    line.workcenter_id.product_id, line.hour)
                analytic_line_obj.create(vals)
            if op_number > 0:
                journal_wk = self.env.ref(
                    'mrp_production_project_estimated_cost.analytic_journal_'
                    'operators', False)
                name = (_('%s-%s-%s') %
                        (self.name, line.routing_wc_line.operation.code,
                         line.workcenter_id.product_id.name))
                vals = self._catch_information_estimated_cost(
                    journal_wk, name, self, line,
                    line.workcenter_id.product_id, op_number)
                vals.update({
                    'estim_average_cost': op_number * op_avg_cost,
                    'estim_standard_cost': op_number * op_avg_cost,
                })
                analytic_line_obj.create(vals)

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
                _('You must define one Analytic Account for this MO: %s') %
                (production.name))
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
