# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    plan = fields.Many2one('procurement.plan', string='Plan')

    @api.multi
    def action_confirm(self):
        proc_obj = self.env['procurement.order']
        res = super(MrpProduction, self).action_confirm()
        for production in self:
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
