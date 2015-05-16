# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _


class WizImportMenuPlanMrp(models.TransientModel):
    _name = 'wiz.import.menu.plan.mrp'

    @api.multi
    def do_import_procurements(self):
        return {'name': _('Import Procurements'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.procurement.from.plan',
                'target': 'new',
                'context': self.env.context,
                }

    @api.multi
    def do_import_procurements_internal(self):
        return {'name': _('Import Procurements'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.procurement.from.plan.mrp',
                'target': 'new',
                'context': self.env.context,
                }
