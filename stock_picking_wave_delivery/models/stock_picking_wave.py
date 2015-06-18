# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    carrier = fields.Many2one('delivery.carrier', 'Carrier')

    @api.multi
    @api.onchange('carrier')
    def onchange_carrier(self):
        self.ensure_one()
        cond = self._get_pickings_domain()
        result = {}
        if cond and self.carrier:
            cond.extend([('carrier_id', '=', self.carrier.id)])
            result['domain'] = {'picking_ids': cond}
        return result
