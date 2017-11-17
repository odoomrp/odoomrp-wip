# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_confirm(self):
        moves = self.filtered(lambda r: r.raw_material_production_id and
                              r.work_order.workcenter_id.machine.location)
        for move in moves:
            location = move.work_order.workcenter_id.machine.location
            if move.location_id.id != location.id:
                move.location_id = location.id
        return super(StockMove, self).action_confirm()
