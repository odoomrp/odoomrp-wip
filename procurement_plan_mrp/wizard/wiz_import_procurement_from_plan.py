# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class WizImportProcurementFromPlan(models.TransientModel):
    _name = "wiz.import.procurement.from.plan"

    @api.multi
    def do_import_procurements(self):
        self.ensure_one()
        plan = self.env['procurement.plan'].browse(
            self.env.context.get("active_id"))
        plan.action_import()
        return True

    @api.multi
    def do_import_procurements_internal(self):
        proc_obj = self.env['procurement.order']
        self.ensure_one()
        plan = self.env['procurement.plan'].browse(
            self.env.context.get("active_id"))
        cond = [('state', 'not in', ('done', 'cancel')),
                ('plan', '=', False)]
        procurements = proc_obj.search(cond)
        procs = procurements.filtered(lambda r: r.location_id.usage == 'internal')
        procs.write({'plan': plan.id,
                     'level': 0})
        return True
