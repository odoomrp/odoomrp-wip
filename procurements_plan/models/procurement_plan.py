# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementPlan(models.Model):

    _name = 'procurement.plan'
    _description = 'Procurement Plan'

    @api.one
    @api.depends('procurement_ids', 'procurement_ids.state')
    def _get_state(self):
        self.state = 'running'
        if not self.procurement_ids:
            self.state = 'draft'
        elif (len(self.procurement_ids.filtered(
                lambda x: x.state == 'draft')) == len(self.procurement_ids)):
            self.state = 'draft'
        elif (len(self.procurement_ids.filtered(
                lambda x: x.state == 'done')) == len(self.procurement_ids)):
            self.state = 'done'
        elif (len(self.procurement_ids.filtered(
                lambda x: x.state == 'cancel')) == len(self.procurement_ids)):
            self.state = 'cancel'

    name = fields.Char(string='Description', required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    sequence = fields.Char(string='Sequence', readonly=True)
    from_date = fields.Date(
        string='From Date', readonly=True,
        states={'draft': [('readonly', False)]})
    to_date = fields.Date(
        string='to Date', readonly=True,
        states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('project.project', string='Project',
                                 required=True)
    procurement_ids = fields.One2many(
        'procurement.order', 'plan', string='Procurements', readonly=True)
    purchase_ids = fields.One2many(
        'purchase.order', 'plan', string='Purchase Orders', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('running', 'Running'),
         ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='Status', compute='_get_state', index=True, store=True,
        track_visibility='onchange', )

    def create(self, cr, uid, data, context=None):
        sequence_obj = self.pool['ir.sequence']
        if context is None:
            context = {}
        if 'sequence' not in data:
            data.update({'sequence': sequence_obj.get(cr, uid,
                                                      'procurement.plan')})
        return super(ProcurementPlan, self).create(cr, uid, data,
                                                   context=context)

    @api.one
    def action_import(self):
        proc_obj = self.env['procurement.order']
        cond = [('state', '!=', 'done'),
                ('plan', '=', False)]
        if self.from_date:
            cond.append(('date_planned', '>=', self.from_date))
        if self.to_date:
            cond.append(('date_planned', '<=', self.to_date))
        procurements = proc_obj.search(cond)
        procurements.write({'plan': self.id})
        return True

    @api.multi
    def button_run(self):
        for plan in self:
            my_context = self.env.context.copy()
            my_context['plan'] = plan.id
            procurements = plan.procurement_ids.filtered(
                lambda x: x.state in ('confirmed', 'exception'))
            procurements.with_context(my_context).run()
        return True

    @api.multi
    def button_cancel(self):
        for plan in self:
            my_context = self.env.context.copy()
            my_context['plan'] = plan.id
            procurements = plan.procurement_ids.filtered(
                lambda x: x.state in ('confirmed', 'exception', 'running'))
            procurements.with_context(my_context).cancel()
        return True

    @api.multi
    def button_check(self):
        for plan in self:
            my_context = self.env.context.copy()
            my_context['plan'] = plan.id
            procurements = plan.procurement_ids.filtered(lambda x: x.state in
                                                         ('running'))
            procurements.with_context(my_context).check()
        return True

    @api.multi
    def button_reset_to_confirm(self):
        for plan in self:
            my_context = self.env.context.copy()
            my_context['plan'] = plan.id
            procurements = plan.procurement_ids.filtered(lambda x: x.state in
                                                         ('cancel'))
            procurements.with_context(my_context).reset_to_confirmed()
        return True

    @api.multi
    def button_calculate_stock(self):
        procurement_obj = self.env['procurement.order']
        user = self.env['res.users'].browse(self.env.uid)
        self.ensure_one()
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'procurement.plan'
        context['plan'] = self.id
        context['procurement_ids'] = self.procurement_ids.ids
        result = procurement_obj.with_context(
            context)._procure_orderpoint_confirm(use_new_cursor=False,
                                                 company_id=user.company_id.id)
        return result
