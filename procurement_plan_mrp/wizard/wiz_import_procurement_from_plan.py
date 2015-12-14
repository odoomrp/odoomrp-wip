# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class WizImportProcurementFromPlan(models.TransientModel):

    _inherit = 'wiz.import.procurement.from.plan'

    @api.multi
    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        self.ensure_one()
        res = super(WizImportProcurementFromPlan, self).onchange_warehouse_id()
        res['domain']['procurement_ids'].append('|')
        res['domain']['procurement_ids'].append(('level', '=', False))
        res['domain']['procurement_ids'].append(('level', '=', 0))
        return res
