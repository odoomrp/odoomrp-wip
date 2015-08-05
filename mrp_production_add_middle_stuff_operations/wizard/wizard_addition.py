
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


class WizProductionProductLine(models.TransientModel):
    _inherit = 'wiz.production.product.line'

    def _def_production_id(self):
        if 'active_model' in self.env.context:
            if self.env.context['active_model'] == 'mrp.production':
                return self.env.context.get('active_id')
            elif self.env.context['active_model'] == (
                    'mrp.production.workcenter.line'):
                mpwl_obj = self.env['mrp.production.workcenter.line']
                active_id = self.env.context.get('active_id', False)
                if active_id:
                    mpwl = mpwl_obj.browse(active_id)
                    return mpwl.production_id.id
        return False

    def _def_work_order_id(self):
        if 'active_model' in self.env.context and (
                self.env.context['active_model'] ==
                'mrp.production.workcenter.line'):
            return self.env.context.get('active_id', False)
        return False

    work_order = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order',
                                 default=_def_work_order_id)
    production_id = fields.Many2one(
        'mrp.production', 'Production Order', select=True,
        default=_def_production_id)

    def _prepare_product_addition(self, product, product_qty, production):
        addition_vals = super(
            WizProductionProductLine, self)._prepare_product_addition(
            product, product_qty, production)
        if self.work_order:
            addition_vals['work_order'] = self.work_order.id
        return addition_vals

    @api.multi
    def add_product(self):
        return super(
            WizProductionProductLine,
            self.with_context(work_order=self.work_order)).add_product()
