# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    waves = fields.Many2many(
        comodel_name='stock.picking.wave',
        relation='rel_wave_package', column1='package_id',
        column2='wave_id', string='Picking Waves')
