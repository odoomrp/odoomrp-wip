# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockPickingTax(models.Model):
    _name = 'stock.picking.tax_breakdown'

    picking = fields.Many2one('stock.picking', string='Picking',
                              ondelete='cascade')
    tax = fields.Many2one('account.tax', string='Tax')
    untaxed_amount = fields.Float(string='Untaxed Amount',
                                  digits=dp.get_precision('Sale Price'))
    taxation_amount = fields.Float(string='Taxation',
                                   digits=dp.get_precision('Sale Price'))
    total_amount = fields.Float(string='Total',
                                digits=dp.get_precision('Sale Price'))


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for move in self.pool['stock.move'].browse(cr, uid, ids,
                                                   context=context):
            result[move.picking_id.id] = True
        return result.keys()

    taxes = fields.One2many('stock.picking.tax_breakdown', 'picking',
                            string='Tax Breakdown')
    amount_untaxed = fields.Float(string='Untaxed Amount',
                                  compute='_amount_all',
                                  digits=dp.get_precision('Sale Price'),
                                  help='The amount without tax.')
    amount_total = fields.Float(string='Total', compute='_amount_all',
                                digits=dp.get_precision('Sale Price'),
                                help='The total amount.')

    @api.multi
    @api.depends('move_lines', 'move_lines.product_qty',
                 'move_lines.product_uos_qty')
    def _amount_all(self):
        for picking in self:
            picking.amount_untaxed = 0.0
            picking.amount_total = 0.0
            val1 = val = 0.0
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
            picking.amount_untaxed = val1
            picking.amount_total = val

    @api.multi
    def _calc_breakdown_taxes(self):
        apportion_obj = self.env['stock.picking.tax_breakdown']
        for picking in self:
            picking.write({'taxes': [(6, 0, [])]})
            for line in picking.move_lines:
                if line.procurement_id and line.procurement_id.sale_line_id:
                    sale_line = line.procurement_id.sale_line_id
                    cur = sale_line.order_id.pricelist_id.currency_id
                    for tax in sale_line.tax_id:
                        price = sale_line.price_unit * (
                            1 - (sale_line.discount or 0.0) / 100.0)
                        taxes = tax.compute_all(
                            price, line.product_qty,
                            sale_line.order_id.partner_invoice_id.id,
                            line.product_id,
                            sale_line.order_id.partner_id)
                        breakdown_ids = apportion_obj.search(
                            [('picking', '=', picking.id),
                             ('tax', '=', tax.id)])
                        subtotal = cur.round(taxes['total'])
                        if not breakdown_ids:
                            line_vals = {
                                'picking': picking.id,
                                'tax': tax.id,
                                'untaxed_amount': subtotal,
                                'taxation_amount':
                                cur.round((subtotal * tax.amount)),
                                'total_amount':
                                cur.round((subtotal * (1 + tax.amount)))
                            }
                            apportion_obj.create(line_vals)
                        else:
                            apport = breakdown_ids[0]
                            untaxed_amount = subtotal + apport.untaxed_amount
                            taxation_amount = cur.round(
                                (untaxed_amount * tax.amount))
                            total_amount = untaxed_amount + taxation_amount
                            apport.write(
                                {'untaxed_amount': untaxed_amount,
                                 'taxation_amount': taxation_amount,
                                 'total_amount': total_amount})
        return True

    @api.multi
    def refresh_tax_breakdown(self):
        return self._calc_breakdown_taxes()


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, data):
        move_id = super(StockMove, self).create(data)
        if 'picking_id' in data:
            picking_obj = self.env['stock.picking']
            picking = picking_obj.browse(data['picking_id'])
            picking._calc_breakdown_taxes()
        return move_id
