# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from dateutil.relativedelta import relativedelta


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _compute_protect_date_planned(self):
        for proc in self:
            proc.protect_date_planned = False
            if (proc.purchase_line_id and
                    proc.purchase_line_id.order_id.state != 'draft'):
                proc.protect_date_planned = True

    plan = fields.Many2one('procurement.plan', string='Plan')
    location_type = fields.Selection([
        ('supplier', 'Supplier Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory'),
        ('procurement', 'Procurement'),
        ('production', 'Production'),
        ('transit', 'Transit Location')],
        string='Location Type', related="location_id.usage", store=True)
    protect_date_planned = fields.Boolean(
        string='Protect Date Planned', compute='_compute_protect_date_planned')

    @api.model
    def create(self, data):
        if 'plan' in self.env.context and 'plan' not in data:
            data['plan'] = self.env.context.get('plan')
        data['is_new'] = False
        procurement = super(ProcurementOrder, self).create(data)
        return procurement

    @api.multi
    def button_remove_plan(self):
        self.ensure_one()
        template_obj = self.env['product.template']
        result = template_obj._get_act_window_dict(
            'procurement_plan.action_procurement_plan')
        result['domain'] = "[('id', '=', " + str(self.plan.id) + ")]"
        result['res_id'] = self.plan.id
        result['view_mode'] = 'form'
        result['views'] = []
        self.plan.write({'procurement_ids': [[3, self.id]]})
        return result

    @api.multi
    def button_run(self, autocommit=False):
        for procurement in self:
            procurement.with_context(plan=procurement.plan.id).run(
                autocommit=autocommit)
            procurement.plan._get_state()
        plans = self.mapped('plan')
        if not plans:
            return True
        res = {'view_type': 'form,tree',
               'res_model': 'procurement.plan',
               'view_id': False,
               'type': 'ir.actions.act_window',
               }
        if len(plans) == 1:
            res.update({'view_mode': 'form',
                        'res_id': plans[0].id,
                        'target': 'current'})
        else:
            res.update({'view_mode': 'tree',
                        'domain': [('id', 'in', plans.ids)],
                        'target': 'new'})
        return res

    @api.multi
    def button_check(self, autocommit=False):
        for procurement in self:
            procurement.with_context(plan=procurement.plan.id).check(
                autocommit=autocommit)
            procurement.plan._get_state()
        plans = self.mapped('plan')
        if not plans:
            return True
        if not plans:
            return True
        res = {'view_type': 'form,tree',
               'res_model': 'procurement.plan',
               'view_id': False,
               'type': 'ir.actions.act_window',
               }
        if len(plans) == 1:
            res.update({'view_mode': 'form',
                        'res_id': plans[0].id,
                        'target': 'current'})
        else:
            res.update({'view_mode': 'tree',
                        'domain': [('id', 'in', plans.ids)],
                        'target': 'new'})
        return res

    @api.multi
    def cancel(self):
        super(ProcurementOrder, self).cancel()
        for procurement in self:
            if procurement.plan:
                procurement.plan._get_state()
        plans = self.mapped('plan')
        if not plans:
            return True
        if not plans:
            return True
        res = {'view_type': 'form,tree',
               'res_model': 'procurement.plan',
               'view_id': False,
               'type': 'ir.actions.act_window',
               }
        if len(plans) == 1:
            res.update({'view_mode': 'form',
                        'res_id': plans[0].id,
                        'target': 'current'})
        else:
            res.update({'view_mode': 'tree',
                        'domain': [('id', 'in', plans.ids)],
                        'target': 'new'})
        return res

    @api.multi
    def reset_to_confirmed(self):
        super(ProcurementOrder, self).reset_to_confirmed()
        for procurement in self:
            if procurement.plan:
                procurement.plan._get_state()
        plans = self.mapped('plan')
        if not plans:
            return True
        if not plans:
            return True
        res = {'view_type': 'form,tree',
               'res_model': 'procurement.plan',
               'view_id': False,
               'type': 'ir.actions.act_window',
               }
        if len(plans) == 1:
            res.update({'view_mode': 'form',
                        'res_id': plans[0].id,
                        'target': 'current'})
        else:
            res.update({'view_mode': 'tree',
                        'domain': [('id', 'in', plans.ids)],
                        'target': 'new'})
        return res

    @api.multi
    def _change_date_planned_from_plan_for_po(self, days_to_sum):
        for proc in self:
            new_date = (fields.Datetime.from_string(proc.date_planned) +
                        (relativedelta(days=days_to_sum)))
            proc.write({'date_planned': new_date})
            if (proc.purchase_line_id and
                    proc.purchase_line_id.order_id.state == 'draft'):
                proc.purchase_line_id.write({'date_planned': new_date})
