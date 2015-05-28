# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
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
