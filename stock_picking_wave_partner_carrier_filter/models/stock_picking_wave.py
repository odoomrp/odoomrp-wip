# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    partner = fields.Many2one('res.partner', 'Partner')
    carrier = fields.Many2one('delivery.carrier', 'Carrier')

    @api.multi
    @api.onchange('partner', 'carrier')
    def onchange_partner_delivery(self):
        self.ensure_one()
        cond = [('state', 'not in', ('done', 'cancel'))]
        if self.partner:
            if self.partner.child_ids:
                ids = map(lambda x: x['id'], self.partner.child_ids)
                cond.extend(['|', ('partner_id', '=', self.partner.id),
                             ('partner_id', 'child_of', ids)])
            else:
                cond.extend([('partner_id', '=', self.partner.id)])
        if self.carrier:
            cond.extend([('carrier_id', '=', self.carrier.id)])
        return {'domain': {'picking_ids': cond}}
