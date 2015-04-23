# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_assign(self):
        super(StockPicking, self).action_assign()
        for picking in self:
            if picking.wave_id:
                picking.wave_id._delete_packages_information()
        return True


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    packages = fields.Many2many(
        comodel_name='stock.quant.package',
        relation='rel_wave_package', column1='wave_id',
        column2='package_id', string='Packages')
    packages_info = fields.One2many(
        "stock.picking.package.kg.lot", "wave", string="Packages Info",
        readonly=True)
    package_totals = fields.One2many(
        "stock.picking.package.total", "wave",
        string="Total UL Packages Info", readonly=True)
    num_packages = fields.Integer(string='# Packages', readonly=True)

    @api.one
    def _delete_packages_information(self):
        self.pickings_operations.unlink()
        self.packages = [(6, 0, [])]
        self.packages_info.unlink()
        self.package_totals.unlink()
        return True

    def _catch_operations(self):
        self.packages = [(6, 0, [])]
        self.packages = [
            operation.result_package_id.id for operation in
            self.pickings_operations if operation.result_package_id]
        self._calculate_package_info()
        self._calculate_package_totals()

    def _calculate_package_info(self):
        if self.packages_info:
            self.packages_info.unlink()
        if self.packages:
            sequence = 0
            for package in self.packages:
                kg_net = sum(x.product_qty for x in
                             self.pickings_operations.filtered(
                                 lambda r: r.result_package_id.id ==
                                 package.id))
                sequence += 1
                vals = {'wave': self.id,
                        'sequence': sequence,
                        'package': package.id,
                        'kg_net': kg_net,
                        'gross_net': kg_net + package.empty_weight
                        }
                lots = False
                for operation in self.pickings_operations.filtered(
                        lambda r: r.result_package_id.id == package.id and
                        r.lot_id):
                    if not lots:
                        lots = operation.lot_id.name
                    else:
                        lots += ', ' + operation.lot_id.name
                vals['lots'] = lots
                self.env['stock.picking.package.kg.lot'].create(vals)

    def _calculate_package_totals(self):
        self.num_packages = 0
        if self.package_totals:
            self.package_totals.unlink()
        if self.packages:
            products_ul = self.env['product.ul'].search([])
            for product_ul in products_ul:
                cont = len(self.packages.filtered(lambda x: x.ul_id.id ==
                                                  product_ul.id))
                if cont > 0:
                    values = {'wave': self.id,
                              'ul': product_ul.id,
                              'quantity': cont}
                    self.env['stock.picking.package.total'].create(values)
                    self.num_packages += cont


class StockPickingPackageKgLot(models.Model):
    _inherit = 'stock.picking.package.kg.lot'

    wave = fields.Many2one('stock.picking.wave', string='Wave')


class StockPickingPackageTotal(models.Model):
    _inherit = 'stock.picking.package.total'

    wave = fields.Many2one('stock.picking.wave', string='Wave')
