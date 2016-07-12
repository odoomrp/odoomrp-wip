# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockPickingTax(models.Model):
    _name = 'stock.picking.tax'

    picking = fields.Many2one(
        comodel_name='stock.picking', string='Picking', ondelete='cascade')
    name = fields.Char(string='Tax Description', required=True)
    base = fields.Float(string='Base', digits=dp.get_precision('Account'))
    amount = fields.Float(string='Amount', digits=dp.get_precision('Account'))
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when displaying a list of picking tax.")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    taxes = fields.One2many(
        comodel_name='stock.picking.tax', string='Taxes',
        compute='_calc_taxes')
    amount_untaxed = fields.Float(
        string='Untaxed Amount', compute='_amount_all',
        digits=dp.get_precision('Sale Price'), help='The amount without tax.')
    amount_tax = fields.Float(
        string='Taxes', compute='_amount_all',
        digits=dp.get_precision('Sale Price'), help='Tax amount')
    amount_total = fields.Float(
        string='Total', compute='_amount_all',
        digits=dp.get_precision('Sale Price'), help='The total amount.')
    currency_id = fields.Many2one(
        string='Sale currency', related='sale_id.currency_id')

    @api.multi
    @api.depends('move_lines', 'move_lines.product_qty',
                 'move_lines.product_uos_qty')
    def _amount_all(self):
        for picking in self:
            picking.amount_untaxed = 0.0
            picking.amount_total = 0.0
            val2 = val1 = val = 0.0
            for line in picking.move_lines:
                if line.procurement_id and line.procurement_id.sale_line_id:
                    sale_line = line.procurement_id.sale_line_id
                    cur = sale_line.order_id.pricelist_id.currency_id
                    price = sale_line.price_unit * (
                        1 - (sale_line.discount or 0.0) / 100.0)
                    taxes = sale_line.tax_id.compute_all(
                        price, line.product_qty,
                        sale_line.order_id.partner_invoice_id.id,
                        line.product_id, sale_line.order_id.partner_id)
                    val1 += cur.round(taxes['total'])
                    val += cur.round(taxes['total_included'])
                    for tax in taxes['taxes']:
                        val2 += tax.get('amount', 0.0)
            picking.amount_untaxed = val1
            picking.amount_tax = val2
            picking.amount_total = val

    @api.multi
    def compute(self, picking):
        if not picking.sale_id:
            return {}
        tax_grouped = {}
        order = picking.sale_id
        currency = order.currency_id.with_context(
            date=order.date_order or fields.Date.context_today(order))
        for move in picking.move_lines:
            sale_line = move.procurement_id.sale_line_id
            price = sale_line.price_unit * (1 - (sale_line.discount or 0.0) /
                                            100)
            taxes = sale_line.tax_id.compute_all(
                price, move.product_qty, move.product_id,
                picking.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'picking': picking.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'base': currency.round(tax['price_unit'] *
                                           move.product_qty),
                    'sequence': tax['sequence'],
                    'base_code_id': tax['base_code_id'],
                    'tax_code_id': tax['tax_code_id'],
                }
                key = (val['tax_code_id'], val['base_code_id'])
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
        return tax_grouped

    @api.multi
    @api.depends('amount_untaxed', 'amount_tax', 'amount_total')
    def _calc_taxes(self):
        taxes = tax_obj = self.env['stock.picking.tax']
        for picking in self:
            picking.taxes.unlink()
            for tax in self.compute(picking).values():
                taxes += tax_obj.create({
                    'picking': tax['picking'],
                    'sequence': tax['sequence'],
                    'name': tax['name'],
                    'base': tax['base'],
                    'amount': tax['amount']})
            picking.taxes = taxes.ids
