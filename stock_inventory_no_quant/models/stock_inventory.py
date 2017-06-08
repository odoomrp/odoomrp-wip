# -*- coding: utf-8 -*-
# © 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    all_products = fields.Boolean(
        default=True, help='If this field is active, the inventory will show '
        'ALL products that comply with the selected filter.',
        string='Show all products')

    def _get_inventory_line_value(self, inventory, line):
        product_line = {}
        product_line['inventory_id'] = inventory.id
        product_line['theoretical_qty'] = 0
        product_line['product_id'] = line.id
        product_line['product_uom_id'] = line.uom_id.id
        product_line['location_id'] = inventory.location_id.id
        return product_line

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = super(StockInventory, self)._get_inventory_lines(inventory)
        if inventory.all_products:
            product_quant = []
            if inventory.filter == 'product' and not len(vals):
                vals.append(self._get_inventory_line_value(
                    inventory, inventory.product_id))
            elif inventory.filter == 'none':
                for prod in vals:
                    product_quant.append(prod['product_id'])
                products = self.env['product.product'].search([
                    ('id', 'not in', product_quant),
                    ('type', '=', 'product')])
                for line in products:
                    vals.append(self._get_inventory_line_value(
                        inventory, line))
        return vals
