# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class WizChangeProcurementDate(models.TransientModel):
    _inherit = 'wiz.change.procurement.date'

    def _take_procurements_to_treat(self, procurement_ids):
        procs = super(WizChangeProcurementDate,
                      self)._take_procurements_to_treat(procurement_ids)
        procs = procs.filtered(lambda x: x.level == 0)
        procs = procs.filtered(lambda x: not x.production_id or (
            x.production_id and x.production_id.state == 'draft'))
        return procs

    @api.multi
    def change_scheduled_date(self):
        super(WizChangeProcurementDate, self).change_scheduled_date()
        route_id = self.env.ref('mrp.route_warehouse0_manufacture').id,
        procurements = self.procurements.filtered(
            lambda x: route_id[0] in x.product_id.route_ids.ids)
        procurements._change_date_planned_from_plan_for_mo(self.days)
