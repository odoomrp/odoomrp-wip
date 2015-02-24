# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    @api.one
    @api.depends('pickings_operations',
                 'pickings_operations.result_package_id')
    def _calculate_packages(self):
        self.packages = [
            operation.result_package_id.id for operation in
            self.pickings_operations if operation.result_package_id]

    pickings_products = fields.One2many(
        'stock.move', 'wave', string='Products')
    pickings_operations = fields.One2many(
        'stock.pack.operation', 'wave', string='Operations')
    packages = fields.Many2many(
        comodel_name='stock.quant.package',
        relation='rel_wave_package', column1='wave_id',
        column2='package_id', string='Packages',
        compute='_calculate_packages', store=True)


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    waves = fields.Many2many(
        comodel_name='stock.picking.wave',
        relation='rel_wave_package', column1='package_id',
        column2='wave_id', string='Picking Waves')


class StockMove(models.Model):
    _inherit = 'stock.move'

    wave = fields.Many2one('stock.picking.wave', related='picking_id.wave_id',
                           string='Picking Wave', store=True)


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    wave = fields.Many2one('stock.picking.wave', related='picking_id.wave_id',
                           string='Picking Wave', store=True)
