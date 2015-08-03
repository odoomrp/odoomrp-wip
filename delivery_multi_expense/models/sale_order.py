# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
import time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    other_expenses = fields.Many2many(
        comodel_name="delivery.carrier",
        relation="sale_delivery_carrier_rel",
        column1="sale_id", column2="delivery_carrier_id",
        string="Expense", copy=False)

    @api.multi
    def delivery_set(self):
        self.ensure_one()
        line_ids = []
        if self.carrier_id:
            line_ids = super(SaleOrder, self).delivery_set()
        for other_expense in self.other_expenses:
            line_ids += self.delivery_set_other_expense(other_expense)
        return line_ids

    @api.multi
    def delivery_set_other_expense(self, other_expense):
        carrier_obj = self.env['delivery.carrier']
        grid_obj = self.env['delivery.grid']
        currency_obj = self.env['res.currency']
        line_obj = self.env['sale.order.line']
        self.ensure_one()
        carrier = carrier_obj.browse(other_expense.id)
        grid_id = carrier.grid_get(self.partner_shipping_id.id)
        if grid_id:
            grid = grid_obj.browse(grid_id)
        else:
            raise exceptions.Warning(
                _('No Grid Available!'),
                _('No grid matching for this expense: %s') %
                (other_expense.name))
        taxes = grid.carrier_id.product_id.taxes_id
        taxes_ids = []
        if self.fiscal_position:
            taxes_ids = self.fiscal_position.map_tax(taxes).mapped('id')
        price_unit = grid.get_price(self, time.strftime('%Y-%m-%d'))
        if self.company_id.currency_id.id != self.pricelist_id.currency_id.id:
            price_unit = currency_obj.with_context(
                date=self.date_order).compute(self.company_id.currency_id.id,
                                              self.pricelist_id.currency_id.id,
                                              price_unit)
        product = grid.carrier_id.product_id
        vals = self._prepare_sale_line_from_other_expense(
            grid, product, price_unit, taxes_ids)
        new_line = line_obj.create(vals)
        return [new_line.id]

    def _prepare_sale_line_from_other_expense(self, grid, product, price_unit,
                                              taxes_ids):
        return {'order_id': self.id,
                'name': grid.carrier_id.name,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'product_id': product.id,
                'price_unit': price_unit[0],
                'tax_id': [(6, 0, taxes_ids)],
                'is_delivery': True
                }
