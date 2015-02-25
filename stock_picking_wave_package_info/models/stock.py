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

    packages = fields.Many2many(
        comodel_name='stock.quant.package',
        relation='rel_wave_package', column1='wave_id',
        column2='package_id', string='Packages',
        compute='_calculate_packages', store=True)
