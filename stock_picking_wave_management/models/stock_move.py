# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    wave = fields.Many2one('stock.picking.wave', related='picking_id.wave_id',
                           string='Picking Wave', store=True)
