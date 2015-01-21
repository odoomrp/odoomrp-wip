# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class WizConfirmHistorification(models.TransientModel):
    _name = "wiz.confirm.historification"

    @api.multi
    def do_confirm_historification(self):
        self.ensure_one()
        mrp_bom_obj = self.env['mrp.bom']
        active_ids = self._context['active_ids']
        for bom in mrp_bom_obj.browse(active_ids):
            bom.write({'active': False, 'state': 'historical',
                       'historical_date': fields.Date.today()})
        return True
