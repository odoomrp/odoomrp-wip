# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    def _create_new_wave(self, new_pickings):
        wave_obj = self.env['stock.picking.wave']
        new_wave = super(StockTransferDetails, self)._create_new_wave(
            new_pickings)
        if 'origin_wave' in self._context:
            origin_wave = wave_obj.browse(self._context['origin_wave'])
            new_wave.update({'carrier': origin_wave.carrier})
        return new_wave
