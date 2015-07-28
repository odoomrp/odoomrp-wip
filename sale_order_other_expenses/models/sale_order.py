# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
import time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    other_expenses = fields.One2many(
        'sale.order.other.expense', 'sale', string='Other expenses',
        copy=False)

    @api.multi
    def delivery_set(self):
        self.ensure_one()
        line_ids = super(SaleOrder, self).delivery_set()
        for other_expense in self.other_expenses:
            line_ids = self.delivery_set_other_expense(line_ids, other_expense)
        return line_ids

    @api.multi
    def delivery_set_other_expense(self, line_ids, other_expense):
        carrier_obj = self.env['delivery.carrier']
        grid_obj = self.env['delivery.grid']
        currency_obj = self.env['res.currency']
        line_obj = self.env['sale.order.line']
        self.ensure_one()
        carrier = carrier_obj.browse(other_expense.expense.id)
        grid_id = carrier.grid_get(self.partner_shipping_id.id)
        if not grid_id:
            raise exceptions.Warning(
                _('No Grid Available!'),
                _('No grid matching for this expense: %s') %
                (other_expense.expense.name))
        grid = grid_obj.browse(grid_id)
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
        new_line = line_obj.create({'order_id': self.id,
                                    'name': grid.carrier_id.name,
                                    'product_uom_qty': 1,
                                    'product_uom': product.uom_id.id,
                                    'product_id': product.id,
                                    'price_unit': price_unit[0],
                                    'tax_id': [(6, 0, taxes_ids)],
                                    'is_delivery': True
                                    })
        line_ids.append(new_line.id)
        return line_ids


class SaleOrderOtherExpense(models.Model):
    _name = 'sale.order.other.expense'
    _rec_name = 'expense'

    sale = fields.Many2one('sale.order', string='Sale order')
    expense = fields.Many2one('delivery.carrier', string='Expense')
