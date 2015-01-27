# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class WizardFilterMrpTask(models.TransientModel):
    _name = 'wizard.filter.mrp.task'
    _description = 'Wizard to filter mrp task'

    mrp_production = fields.Many2one(
        "mrp.production", string="Production Order")
    wk_order = fields.Many2one(
        "mrp.production.workcenter.line", string="Work Order")
    task = fields.Many2one(
        "project.task", string="Project Task")
    user = fields.Many2one("res.users", string="User")
    name = fields.Char(string='Work summary')
    hours = fields.Float(string='Time Spent')

    @api.multi
    @api.onchange('mrp_production')
    def production_onchange(self):
        self.ensure_one()
        wc_ids = []
        domain_wk_order = False
        domain_task = False
        if self.mrp_production:
            domain_task = [('mrp_production_id', '=', self.mrp_production.id)]
            for wc_line in self.mrp_production.workcenter_lines:
                wc_ids.append(wc_line.id)
        if wc_ids:
            domain_task += [('wk_order', 'in', wc_ids)]
            domain_wk_order = [('id', 'in', wc_ids)]
        return {'domain': {'wk_order': domain_wk_order,
                           'task': domain_task}}

    @api.multi
    @api.onchange('wk_order')
    def wk_order_onchange(self):
        self.ensure_one()
        domain_task = False
        if self.wk_order:
            domain_task = [('wk_order', '=', self.wk_order.id)]
        return {'domain': {'task': domain_task}}

    @api.one
    @api.onchange('task')
    def task_onchange(self):
        self.mrp_production = self.task.mrp_production_id.id or False
        self.wk_order = self.task.wk_order.id or False

    def mrp_task_open_window(self, cr, uid, ids, context=None):
        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']
        result_context = {}
        if context is None:
            context = {}
        result = mod_obj.get_object_reference(
            cr, uid, 'mrp_wizard_filter_task',
            'action_project_task_work_filter_tree2')
        res_id = result and result[1] or False
        result = act_obj.read(cr, uid, [res_id], context=context)[0]
        data = self.browse(cr, uid, ids, context=context)
        domain = []
        if data.mrp_production:
            domain.append(('mrp_production_id', '=', data.mrp_production.id))
            result_context.update({'mrp_production_id':
                                   data.mrp_production.id})
        if data.wk_order:
            domain.append(('wk_order', '=', data.wk_order.id))
            result_context.update({'wk_order': data.wk_order.id})
        if data.task:
            domain.append(('task_id', '=', data.task.id))
            result_context.update({'task_id': data.task.id})
        if data.user:
            domain.append(('user_id', '=', data.user.id))
            result_context.update({'user_id': data.user.id})
        result['domain'] = domain
        result['context'] = str(result_context)
        return result

    @api.multi
    def mrp_create_task_analytic(self):
        task_work_obj = self.env['project.task.work']
        self.ensure_one()
        if not self.task:
            raise exceptions.Warning(
                _('Error!: You must select a task'))
        if not self.user:
            raise exceptions.Warning(
                _('Error!: You must select a user'))
        if not self.name:
            raise exceptions.Warning(
                _('Error!: You must enter Work summary'))
        if not self.hours:
            raise exceptions.Warning(
                _('Error!: You must enter the hours to work/impute'))
        vals = {'date': fields.Datetime.now(),
                'name': self.name,
                'hours': self.hours,
                'task_id': self.task.id,
                'user_id': self.user.id
                }
        task_work_obj.create(vals)
        return self.mrp_task_open_window()
