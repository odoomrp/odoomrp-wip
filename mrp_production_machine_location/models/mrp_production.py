# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_confirm(self):
        result = super(MrpProduction, self).action_confirm()
        for prod in self:
            workcenter_lines = prod.workcenter_lines.filtered(
                lambda r: r.do_production)
            workcenter_line =\
                workcenter_lines.sorted(key=lambda x: x.sequence)[-1:]
            location = workcenter_line.workcenter_id.machine.location
            if location:
                prod.move_created_ids.write({'location_dest_id': location.id})
        return result

    @api.model
    def _make_production_consume_line(self, line):
        move_id = super(MrpProduction,
                        self)._make_production_consume_line(line)
        if line.work_order.workcenter_id.machine.location and move_id:
            move = self.env['stock.move'].browse(move_id)
            move.location_id =\
                line.work_order.workcenter_id.machine.location
        return move_id

    @api.model
    def _make_consume_line_from_data(self, production, product, uom_id, qty,
                                     uos_id, uos_qty):
        move_id = super(MrpProduction, self)._make_consume_line_from_data(
            production, product, uom_id, qty, uos_id, uos_qty)
        work_order = self.env.context.get('default_work_order', False)
        if work_order and work_order.workcenter_id.machine.location:
            move = self.env['stock.move'].browse(move_id)
            move.location_id = work_order.workcenter_id.machine.location
        return move_id
