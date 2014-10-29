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

    estim_standard_cost = fields.Float(string='Estimate Standard Cost')
    estim_average_cost = fields.Float(string='Estimate Average Cost')
    last_purchase_cost = fields.Float(string='Last Purchase Cost')
    last_sale_price = fields.Float(string='Last Sale Price')

    @api.one
    @api.model
    def action_confirm(self):
        analytic_line_obj = self.env['account.analytic.line']
        res = super(MrpProduction, self).action_confirm()
        if self.state == 'draft':
            return res
        journal = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_estimated'
            '_materials', False)
        for line in self.product_lines:
            name = (self.name + '-' +
                    line.work_order.routing_wc_line.operation.code)
            vals = self._cath_information_estimated_cost(
                journal, name, line.product_id, line.product_qty)
            analytic_line_obj.create(vals)
        journal = self.env.ref(
            'mrp_production_project_estimated_cost.analytic_journal_estimated'
            '_machines', False)
        for line in self.workcenter_lines:
            if line.cycle and line.workcenter_id.product_id:
                name = (self.name + '-' + line.routing_wc_line.operation.code
                        + '-C-' + line.workcenter_id.name)
                vals = self._cath_information_estimated_cost(
                    journal, name, line.workcenter_id.product_id,
                    line.cycle)
                analytic_line_obj.create(vals)
            if line.hour and line.workcenter_id.product_id:
                name = (self.name + '-' + line.routing_wc_line.operation.code
                        + '-H-' + line.workcenter_id.name)
                vals = self._cath_information_estimated_cost(
                    journal, name, line.workcenter_id.product_id,
                    line.hour)
                analytic_line_obj.create(vals)
            for op_wc_line in line.routing_wc_line.op_wc_lines:
                if (op_wc_line.workcenter.id ==
                    line.workcenter_id.id and
                    line.workcenter_id.product_id and
                        op_wc_line.op_number > 0):
                    journal = self.env.ref(
                        'mrp_production_project_estimated_cost.analytic_'
                        'journal_estimated_operators', False)
                    name = (self.name + '-' +
                            line.routing_wc_line.operation.code
                            + line.workcenter_id.product_id.name)
                    vals = self._cath_information_estimated_cost(
                        journal, name,
                        line.workcenter_id.product_id, line.hour)
                    cont = 1
                    while cont <= op_wc_line.op_number:
                        analytic_line_obj.create(vals)
                        cont += 1
        return res

    def _cath_information_estimated_cost(self, journal, name, product_id, qty):
        analytic_line_obj = self.env['account.analytic.line']
        general_account = (product_id.property_account_income or
                           product_id.categ_id.property_account_income_categ
                           or False)
        if not general_account:
            raise exceptions.Warning(
                _('You must define Income account in the product "%s", or in'
                  ' the product category') % (product_id.name))
        vals = {'name': name,
                'account_id': self.analytic_account_id.id,
                'journal_id': journal.id,
                'user_id': self._uid,
                'date': analytic_line_obj._get_default_date(),
                'product_id': product_id.id,
                'unit_amount': qty,
                'product_uom_id': product_id.uom_id.id,
                'general_account_id': general_account.id
                }
        return vals
