# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class WizPickingToWave(models.TransientModel):
    _name = 'wiz.picking.to.wave'
    _description = 'Wizard picking to wave'

    wave = fields.Many2one(
        'stock.picking.wave', string='Picking Wave', required=True)

    @api.one
    def do_picking_to_wave(self):
        package_preparation_obj = self.env['stock.picking.package.preparation']
        package_preparation = package_preparation_obj.browse(
            self._context['active_id'])
        package_preparation.picking_ids.write({'wave_id': self.wave.id})
        return True
