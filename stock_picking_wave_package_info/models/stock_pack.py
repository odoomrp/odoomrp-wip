# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    wave = fields.Many2one('stock.picking.wave', related='picking_id.wave_id',
                           string='Picking Wave', store=True)
