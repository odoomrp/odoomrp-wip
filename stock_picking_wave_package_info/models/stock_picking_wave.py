# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockPickingPackageWeightLot(models.Model):
    _inherit = 'stock.picking.package.weight.lot'

    wave = fields.Many2one('stock.picking.wave', string='Wave')


class StockPickingPackageTotal(models.Model):
    _inherit = 'stock.picking.package.total'

    wave = fields.Many2one('stock.picking.wave', string='Wave')


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    @api.one
    @api.depends('pickings_operations',
                 'pickings_operations.result_package_id')
    def _calc_wave_packages(self):
        self.packages = self.pickings_operations.mapped('result_package_id')

    @api.one
    @api.depends('packages', 'packages.ul_id')
    def _calc_wave_packages_info(self):
        pack_weight = self.env['stock.picking.package.weight.lot']
        pack_weight_obj = self.env['stock.picking.package.weight.lot']
        pack_total = self.env['stock.picking.package.total']
        pack_total_obj = self.env['stock.picking.package.total']
        sequence = 0
        for package in self.packages:
            sequence += 1
            package_operations = self.pickings_operations.filtered(
                lambda r: r.result_package_id == package)
            total_weight = 0.0
            for pack_operation in package_operations:
                total_weight += (pack_operation.product_qty *
                                 pack_operation.product_id.weight)
            vals = {
                'wave': self.id,
                'sequence': sequence,
                'package': package.id,
                'lots': [(6, 0, (package.quant_ids.mapped('lot_id').ids or
                                 package_operations.mapped('lot_id').ids))],
                'net_weight': total_weight,
                'gross_weight': total_weight + package.empty_weight,
            }
            pack_weight += pack_weight_obj.create(vals)
        if self.packages:
            for product_ul in self.env['product.ul'].search([]):
                cont = len(self.packages.filtered(
                    lambda x: x.ul_id.id == product_ul.id))
                if cont:
                    vals = {
                        'wave': self.id,
                        'ul': product_ul.id,
                        'quantity': cont,
                    }
                    pack_total += pack_total_obj.create(vals)
        self.packages_info = pack_weight
        self.package_totals = pack_total
        self.num_packages = sum(x.quantity for x in self.package_totals)

    packages = fields.Many2many(
        comodel_name='stock.quant.package', string='Packages',
        compute='_calc_wave_packages')
    packages_info = fields.One2many(
        comodel_name='stock.picking.package.weight.lot', inverse_name='wave',
        string='Packages Info', compute='_calc_wave_packages_info')
    package_totals = fields.One2many(
        comodel_name='stock.picking.package.total', inverse_name='wave',
        string='Total UL Packages Info', compute='_calc_wave_packages_info')
    num_packages = fields.Integer(
        string='# Packages', compute='_calc_wave_packages_info')
