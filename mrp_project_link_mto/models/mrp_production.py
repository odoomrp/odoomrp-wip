# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_confirm(self):
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        result = super(MrpProduction, self).action_confirm()
        for record in self:
            # Refresh MTO procurement data
            main_project = record.project_id.id
            for move in record.move_lines:
                if mto_record in move.product_id.route_ids:
                    move.main_project_id = main_project
                    procurements = self.env['procurement.order'].search(
                        [('move_dest_id', '=', move.id)])
                    procurements.write({'main_project_id': main_project})
                    procurements.refresh()
                    procurements.set_main_project()
        return result
