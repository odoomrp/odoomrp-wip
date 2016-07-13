# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


class ProcurementPlan(models.Model):

    _name = 'procurement.plan'
    _description = 'Procurement Plan'
    _inherit = ['mail.thread']
    _rec_name = 'sequence'

    @api.multi
    @api.depends('procurement_ids', 'procurement_ids.state')
    def _get_state(self):
        for plan in self:
            plan.state = 'running'
            if not plan.procurement_ids:
                plan.state = 'draft'
            elif all(x.state == 'cancel' for x in plan.procurement_ids):
                plan.state = 'cancel'
            elif (len(plan.procurement_ids.filtered(
                    lambda x: x.state == 'cancel')) > 1):
                plan.state = 'draft'
            elif all(x.state == 'done' for x in plan.procurement_ids):
                plan.state = 'done'

    @api.multi
    def _get_plan_sequence(self):
        return self.env['ir.sequence'].next_by_code('procurement.plan')

    @api.multi
    def _count_num_procurements(self):
        for plan in self:
            plan.num_procurements = len(plan.procurement_ids)

    @api.multi
    @api.depends('procurement_ids', 'procurement_ids.state')
    def _calc_plan_purchases(self):
        for plan in self:
            purchases = set(plan.mapped('procurement_ids.purchase_id'))
            plan.purchase_ids = [(6, 0, [purchase.id for purchase in
                                         purchases])]

    name = fields.Char(string='Description', required=True, readonly=True,
                       states={'draft': [('readonly', False)]},
                       default="/")
    sequence = fields.Char(string='Sequence', readonly=True,
                           default=_get_plan_sequence)
    from_date = fields.Date(
        string='From Date', readonly=True,
        states={'draft': [('readonly', False)]})
    to_date = fields.Date(
        string='to Date', readonly=True,
        states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=True)
    project_id = fields.Many2one(
        'project.project', string='Project', required=True)
    procurement_ids = fields.One2many(
        'procurement.order', 'plan', string='Procurements', readonly=True)
    num_procurements = fields.Integer(
        compute="_count_num_procurements", string="Procurements")
    purchase_ids = fields.Many2many(
        comodel_name='purchase.order',
        relation='rel_procurement_plan_purchase_order', column1='plan_id',
        column2='purchase_id', string='Purchase Orders', copy=False,
        store=True, compute='_calc_plan_purchases', readonly=False)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('running', 'Running'),
         ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='Status', compute='_get_state', index=True, store=True,
        track_visibility='onchange', )

    @api.multi
    def button_load_sales(self):
        self.ensure_one()
        if not self.from_date:
            raise exceptions.Warning(
                _('Error!: You must enter from date.'))
        if not self.to_date:
            raise exceptions.Warning(
                _('Error!: You must enter to date.'))
        if self.from_date > self.to_date:
            raise exceptions.Warning(
                _('Error!: End date is lower than start date.'))
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'procurement.plan'
        return {'name': _('Load Sales'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.load.sale.from.plan',
                'target': 'new',
                'context': context,
                }

    @api.multi
    def button_load_purchases(self):
        self.ensure_one()
        if not self.from_date:
            raise exceptions.Warning(
                _('Error!: You must enter from date.'))
        if not self.to_date:
            raise exceptions.Warning(
                _('Error!: You must enter to date.'))
        if self.from_date > self.to_date:
            raise exceptions.Warning(
                _('Error!: End date is lower than start date.'))
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'procurement.plan'
        return {'name': _('Load Purchases'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.load.purchase.from.plan',
                'target': 'new',
                'context': context,
                }

    @api.multi
    def button_run(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(
                lambda x: x.state in ('confirmed', 'exception'))
            procurements.with_context(plan=plan.id).run()
        return True

    @api.multi
    def button_cancel(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(
                lambda x: x.state in ('confirmed', 'exception', 'running'))
            procurements.with_context(plan=plan.id).cancel()
            plan._get_state()
        return True

    @api.multi
    def button_check(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(lambda x: x.state in
                                                         ('running'))
            procurements.with_context(plan=plan.id).check()
        return True

    @api.multi
    def button_reset_to_confirm(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(lambda x: x.state in
                                                         ('cancel'))
            procurements.with_context(plan=plan.id).reset_to_confirmed()
        return True
