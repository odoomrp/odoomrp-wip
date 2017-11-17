# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class WizImportProcurementFromPlan(models.TransientModel):

    _name = 'wiz.import.procurement.from.plan'

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='to Date')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    procurement_ids = fields.Many2many(
        comodel_name="procurement.order",
        relation="import_from_plan_procurement_rel",
        column1="wiz_import_plan_id", column2="procurement_id",
        string="Procurements")

    @api.model
    def default_get(self, var_fields):
        super(WizImportProcurementFromPlan, self).default_get(var_fields)
        plan = self.env['procurement.plan'].browse(
            self.env.context['active_id'])
        return {'from_date': plan.from_date,
                'to_date': plan.to_date,
                'warehouse_id': plan.warehouse_id.id}

    @api.multi
    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        self.ensure_one()
        cond = [('warehouse_id', '=', self.warehouse_id.id),
                ('state', 'not in', ('cancel', 'done')),
                ('location_type', '=', 'internal'),
                ('plan', '=', False)]
        if self.from_date:
            cond.append(('date_planned', '>=', self.from_date))
        if self.to_date:
            cond.append(('date_planned', '<=', self.to_date))
        return {'domain': {'procurement_ids': cond}}

    @api.multi
    def import_procurements(self):
        self.ensure_one()
        self.procurement_ids.write({'plan': self.env.context['active_id']})
        plan = self.env['procurement.plan'].browse(
            self.env.context['active_id'])
        if plan.procurement_ids:
            sorted_procs = sorted(plan.procurement_ids,
                                  key=lambda l: l.date_planned, reverse=True)
            plan.to_date = sorted_procs[0].date_planned
            plan.from_date = sorted_procs[len(sorted_procs)-1].date_planned
        return True
