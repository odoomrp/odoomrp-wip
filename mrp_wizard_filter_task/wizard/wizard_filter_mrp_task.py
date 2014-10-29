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
from openerp import models, fields


class WizardFilterMrpTask(models.TransientModel):
    _name = 'wizard.filter.mrp.task'
    _description = 'Wizard to filter mrp task'

    mrp_production = fields.Many2one(
        "mrp.production", string="Production Order")
    wk_order = fields.Many2one(
        "mrp.production.workcenter.line", string="Work Order")
    user = fields.Many2one("res.users", string="User")

    def mrp_task_open_window(self, cr, uid, ids, context=None):
        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']
        result_context = {}
        if context is None:
            context = {}
        result = mod_obj.get_object_reference(
            cr, uid, 'mrp_wizard_filter_task',
            'action_project_task_filter_tree2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        data = self.browse(cr, uid, ids, context=context)
        domain = []
        if data.mrp_production:
            domain.append(('mrp_production_id', '=', data.mrp_production.id))
            result_context.update({'mrp_production_id':
                                   data.mrp_production.id})
        if data.wk_order:
            domain.append(('wk_order', '=', data.wk_order.id))
            result_context.update({'wk_order': data.wk_order.id})
        if data.user:
            domain.append(('user', '=', data.user.id))
            result_context.update({'user': data.user.id})
        result['domain'] = domain
        result['context'] = str(result_context)
        return result
