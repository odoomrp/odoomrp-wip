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
