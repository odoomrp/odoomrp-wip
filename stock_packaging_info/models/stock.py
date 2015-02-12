# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.one
    @api.depends('product_id', 'product_uom_qty',
                 'product_id.attribute_value_ids',
                 'product_id.attribute_value_ids.attribute_id',
                 'product_id.attribute_value_ids.attribute_id.is_package',
                 'product_id.attribute_value_ids.numeric_value')
    def _compute_packages_number(self):
        self.packages_number = 0
        if self.product_id and self.product_uom_qty:
            for value in self.product_id.attribute_value_ids:
                if value.attribute_id.is_package and value.numeric_value:
                    self.packages_number = (
                        self.product_uom_qty / value.numeric_value)

    packages_number = fields.Float(
        string='# Packages', compute='_compute_packages_number',
        store=True)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    @api.depends('product_id', 'qty',
                 'product_id.attribute_value_ids',
                 'product_id.attribute_value_ids.attribute_id',
                 'product_id.attribute_value_ids.attribute_id.is_package',
                 'product_id.attribute_value_ids.numeric_value')
    def _compute_packages_number(self):
        self.packages_number = 0
        if self.product_id and self.qty:
            for value in self.product_id.attribute_value_ids:
                if value.attribute_id.is_package and value.numeric_value:
                    self.packages_number = self.qty / value.numeric_value

    packages_number = fields.Float(
        string='# Packages', compute='_compute_packages_number',
        store=True)
