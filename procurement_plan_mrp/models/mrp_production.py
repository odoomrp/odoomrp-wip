# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    plan = fields.Many2one('procurement.plan', string='Plan')

    @api.multi
    def action_confirm(self):
        proc_obj = self.env['procurement.order']
        res = super(MrpProduction, self).action_confirm()
        for production in self:
            if (production.project_id and production.plan and not
                    production.sale_id):
                old_project = production.plan.project_id
                if old_project.id != production.project_id.id:
                    production.plan.project_id = production.project_id.id
                    old_project.unlink()
            cond = [('production_id', '=', production.id)]
            proc = proc_obj.search(cond, limit=1)
            if proc:
                self._treat_procurements_reservations(proc)
        return res

    @api.multi
    def _treat_procurements_reservations(self, proc):
        self.ensure_one()
        reservation_obj = self.env['stock.reservation']
        proc_obj = self.env['procurement.order']
        level = 1
        if proc.level:
            level = proc.level + 1
        cond = [('parent_procurement_id', 'child_of', proc.id),
                ('id', '!=', proc.id),
                ('level', '=', level)]
        procs = proc_obj.search(cond)
        if procs:
            for proc in procs:
                cond = [('procurement_from_plan', '=', proc.id)]
                reservation = reservation_obj.search(cond, limit=1)
                reservation.release()

    @api.multi
    def button_create_plan(self):
        plan_obj = self.env['procurement.plan']
        proc_obj = self.env['procurement.order']
        project_obj = self.env['project.project']
        warehouse_obj = self.env['stock.warehouse']
        for production in self:
            project_vals = {
                'name': _('Generated from MO: ') + production.name}
            project = project_obj.create(project_vals)
            proc_vals = {
                'name': _('Generated from MO: ') + production.name,
                'product_id': production.product_id.id,
                'location_id': production.location_src_id.id,
                'product_qty': production.product_qty,
                'product_uom': production.product_uom.id}
            proc = proc_obj.create(proc_vals)
            date_planned = fields.Datetime.from_string(
                production.date_planned).date()
            warehouse = warehouse_obj.search([], limit=1)
            plan_vals = {
                'name': _('Generated from MO: ') + production.name,
                'warehouse_id': warehouse.id,
                'from_date': date_planned,
                'to_date': date_planned,
                'project_id': project.id,
                'procurement_ids': [(4, proc.id)]}
            plan = plan_obj.create(plan_vals)
            production.plan = plan
            proc._create_procurement_lower_levels(plan.id)
            for procurement in plan.procurement_ids:
                if procurement.show_button_create:
                    procurement.button_create_lower_levels()
