# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementPlan(models.Model):

    _name = 'procurement.plan'
    _description = 'Procurement Plan'
    _rec_name = 'sequence'

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

    @api.multi
    def _get_plan_sequence(self):
        sequence = self.env['ir.sequence'].next_by_code('procurement.plan')
        return sequence

    @api.one
    def _count_num_procurements(self):
        self.num_procurements = len(self.procurement_ids)

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
    project_id = fields.Many2one('project.project', string='Project',
                                 required=True)
    procurement_ids = fields.One2many(
        'procurement.order', 'plan', string='Procurements', readonly=True)
    num_procurements = fields.Integer(
        compute="_count_num_procurements", string="Procurements")
    purchase_ids = fields.Many2many(
        comodel_name='purchase.order',
        relation='rel_procurement_plan_purchase_order', column1='plan_id',
        column2='purchase_id', string='Purchase Orders', copy=False)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('running', 'Running'),
         ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='Status', compute='_get_state', index=True, store=True,
        track_visibility='onchange', )

    @api.multi
    def action_import(self):
        self.ensure_one()
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
            procurements = plan.procurement_ids.filtered(
                lambda x: x.state in ('confirmed', 'exception'))
            procurements.with_context(plan=plan.id).run()
            plan._catch_purchases()
        return True

    @api.multi
    def button_cancel(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(
                lambda x: x.state in ('confirmed', 'exception', 'running'))
            procurements.with_context(plan=plan.id).cancel()
        return True

    @api.multi
    def button_check(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(lambda x: x.state in
                                                         ('running'))
            procurements.with_context(plan=plan.id).check()
            plan._catch_purchases()
        return True

    @api.multi
    def button_reset_to_confirm(self):
        for plan in self:
            procurements = plan.procurement_ids.filtered(lambda x: x.state in
                                                         ('cancel'))
            procurements.with_context(plan=plan.id).reset_to_confirmed()
        return True

    @api.multi
    def button_calculate_stock(self):
        procurement_obj = self.env['procurement.order']
        user = self.env['res.users'].browse(self.env.uid)
        self.ensure_one()
        result = procurement_obj.with_context(
            active_model='procurement_plan', active_id=self.id,
            procurement_ids=self.procurement_ids, active_ids=[self.id],
            plan=self.id)._procure_orderpoint_confirm(
                use_new_cursor=False,
                company_id=user.company_id.id)
        self._catch_purchases()
        cond = [('state', 'not in', ('cancel', 'done'))]
        self.search(cond)._get_state()
        return result

    @api.one
    def _catch_purchases(self):
        purchases = set(self.procurement_ids.mapped('purchase_id'))
        self.purchase_ids = [(6, 0, [purchase.id for purchase in
                                     purchases])]
