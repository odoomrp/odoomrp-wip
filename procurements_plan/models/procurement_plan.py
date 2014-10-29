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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class ProcurementPlan(models.Model):

    _name = 'procurement.plan'
    _description = 'Procurement Plan'

    name = fields.Char(string='Description', required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    sequence = fields.Char(string='Sequence', readonly=True)
    from_date = fields.Date(
        string='From Date', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    to_date = fields.Date(
        string='to Date', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('project.project', string='Project',
                                 required=True)
    procurement_ids = fields.One2many(
        'procurement.order', 'plan', string='Procurements', readonly=True)
    purchase_ids = fields.One2many(
        'purchase.order', 'plan', string='Purchases', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled'), ],
        string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange')

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
        cond = [('date_planned', '>=', self.from_date),
                ('date_planned', '<=', self.to_date),
                ('plan', '=', False),
                ('state', 'in', ('running', 'confirmed'))]
        procurements = proc_obj.search(cond)
        if procurements:
            procurements.write({'plan': self.id})
        return True

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.one
    def action_run(self):
        proc_obj = self.env['procurement.order']
        move_obj = self.env['stock.move']
        comp_obj = self.env['procurement.order.compute.all']
        plan = self
        if not plan.procurement_ids:
            raise except_orm(_('Error!'),
                             _("No procurements to treat"))
        my_proc = []
        for proc in plan.procurement_ids:
            my_proc.append(proc.id)
        cond = [('state', '=', 'confirmed'),
                ('id', 'not in', my_proc),
                ('plan', '=', False)]
        procurements = proc_obj.search(cond)
        if procurements:
            vals = {'state': 'cancel', 'origin_state': 'confirmed'}
            procurements.write(vals)
        cond = [('state', '=', 'running'),
                ('id', 'not in', my_proc),
                ('plan', '=', False)]
        procurements = proc_obj.search(cond)
        if procurements:
            vals = {'state': 'cancel', 'origin_state': 'running'}
            procurements.write(vals)
        self.env.cr.commit()
        comp_obj.with_context(plan=plan.id)._procure_calculation_all()
        cond = [('origin_state', '=', 'confirmed')]
        procurements = proc_obj.search(cond)
        if procurements:
            vals = {'state': 'confirmed', 'origin_state': False}
            procurements.write(vals)
        cond = [('origin_state', '=', 'running')]
        procurements = proc_obj.search(cond)
        if procurements:
            vals = {'state': 'running', 'origin_state': False}
            procurements.write(vals)
        return self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        for proc in self:
            if proc.procurement_ids:
                proc.procurement_ids.write({'plan': False})
        return self.write({'state': 'cancel'})
