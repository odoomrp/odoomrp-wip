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
            if self.partner.parent_id:
                cond.extend(['|', ('partner_id', '=', self.partner.id),
                             ('partner_id', '=', self.partner.parent_id.id)])
            else:
                cond.extend([('partner_id', '=', self.partner.id)])
        if self.carrier:
            cond.extend([('carrier_id', '=', self.carrier.id)])
        print '*** cond: ' + str(cond)
        return {'domain': {'picking_ids': cond}}
