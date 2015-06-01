# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.one
    def _get_waves(self):
        self.waves = self.env['stock.pack.operation'].search(
            [('result_package_id', '=', self.id)]).mapped('wave')

    waves = fields.Many2many(
        comodel_name='stock.picking.wave', string='Picking Waves',
        compute='_get_waves')
