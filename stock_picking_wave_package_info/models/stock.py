# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    packages = fields.Many2many(
        comodel_name='stock.quant.package',
        relation='rel_wave_package', column1='wave_id',
        column2='package_id', string='Packages')

    def _catch_operations(self):
        self.packages = [
            operation.result_package_id.id for operation in
            self.pickings_operations if operation.result_package_id]
