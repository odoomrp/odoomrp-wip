# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from lxml import etree


class PurchaseOrderLineSubtotal(models.Model):
    _name = 'purchase.order.line.subtotal'

    @api.one
    def _calculate_subtotal(self):
        price = (self.line_id.price_unit *
                 (1 - (self.item_id.discount or 0.0) / 100) *
                 (1 - (self.item_id.discount2 or 0.0) / 100))
        qty = self.line_id.product_qty
        if self.item_id.offer_id:
            total = (self.item_id.offer_id.free_qty +
                     self.item_id.offer_id.paid_qty)
            qty = round((qty / total) * self.item_id.offer_id.paid_qty)
        taxes = self.line_id.taxes_id.compute_all(
            price, qty, self.line_id.product_id, self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        self.subtotal = cur.round(taxes['total'])

    line_id = fields.Many2one(
        comodel_name='purchase.order.line', string='Line', ondelete='cascade')
    purchase_id = fields.Many2one(
        comodel_name='purchase.order', string='Purchase Order',
        related='line_id.order_id', store=True)
    item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string='Pricelist Item',
        ondelete='cascade')
    subtotal = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        compute='_calculate_subtotal')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _calc_price_subtotal(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        return price * (1 - (self.discount2 or 0.0) / 100.0)

    def _calc_qty(self):
        qty = self.product_qty
        if self.offer_id:
            total = self.offer_id.free_qty + self.offer_id.paid_qty
            qty = (qty // total) * self.offer_id.paid_qty + (qty % total)
        return qty

    @api.one
    def _amount_line(self):
        new_price_subtotal = self._calc_price_subtotal()
        qty = self._calc_qty()
        taxes = self.taxes_id.compute_all(
            new_price_subtotal, qty, self.product_id,
            self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        self.price_subtotal = cur.round(taxes['total'])

    def _get_possible_item_ids(self, pricelist_id, product_id=False, qty=0):
        item_obj = self.env['product.pricelist.item']
        item_ids = item_obj.domain_by_pricelist(
            pricelist_id, product_id=product_id, qty=qty)
        return item_ids

    @api.one
    @api.depends('product_id', 'product_qty',
                 'order_id.pricelist_id')
    def _get_possible_items(self):
        item_ids = self._get_possible_item_ids(
            self.order_id.pricelist_id.id, product_id=self.product_id.id,
            qty=self.product_qty)
        self.possible_item_ids = [(6, 0, item_ids)]

    discount2 = fields.Float(
        string='Discount 2 (%)', digits=dp.get_precision('Discount'),
        default=0.0)
    offer_id = fields.Many2one(
        comodel_name='product.pricelist.item.offer', string='Offer')
    item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string='Pricelist Item')
    possible_item_ids = fields.Many2many(
        comodel_name='product.pricelist.item',
        compute='_get_possible_items')
    subtotal_ids = fields.One2many(
        comodel_name='purchase.order.line.subtotal', inverse_name='line_id',
        string='Subtotals by pricelist')
    price_subtotal = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        compute='_amount_line')

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         _('Second discount must be lower than 100%.')),
    ]

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(PurchaseOrderLine, self).default_get(cr, uid, fields_list,
                                                         context=context)
        item_obj = self.pool['product.pricelist.item']
        if context.get('pricelist_id'):
            item_id = item_obj.get_best_pricelist_item(
                cr, uid, context['pricelist_id'], context=context)
            res.update({'item_id': item_id})
        return res

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state)
        if product_id:
            item_obj = self.env['product.pricelist.item']
            item_id = item_obj.get_best_pricelist_item(
                pricelist_id, product_id=product_id, qty=qty)
            res['value'].update({'item_id': item_id})
            res['value']['price_unit'] = item_obj.browse(
                item_id).price_get(product_id, qty, partner_id, uom_id)[0]
            if 'domain' not in res:
                res['domain'] = {}
            res['domain'].update({'item_id':
                                  [('id', 'in',
                                    self._get_possible_item_ids(
                                        pricelist_id, product_id=product_id,
                                        qty=qty))]})
        return res

    @api.one
    @api.onchange('item_id')
    def onchange_item_id(self):
        if self.item_id:
            self.discount = self.item_id.discount
            self.discount2 = self.item_id.discount2
            self.offer_id = self.item_id.offer.id
            if self.product_id:
                self.price_unit = self.item_id.price_get(
                    self.product_id.id, self.product_qty,
                    self.order_id.partner_id.id, self.product_id.uom_id.id)[0]


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            eview = etree.fromstring(res['arch'])

            def _check_rec(eview):
                if eview.attrib.get('name', '') == 'order_line':
                    context = eview.attrib.get(
                        'context', '{}').replace(
                        '}', ",'pricelist_id':pricelist_id}").replace(
                        '{,', '{')
                    eview.set('context', context)
                for child in eview:
                    _check_rec(child)
                return True

            _check_rec(eview)
            res['arch'] = etree.tostring(eview)
        return res

    @api.model
    def _amount_line_tax(self, line):
        val = 0.0
        new_price_subtotal = line._calc_price_subtotal()
        qty = line._calc_qty()
        for c in line.taxes_id.compute_all(new_price_subtotal,
                                           qty, line.product_id,
                                           line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    @api.multi
    def onchange_pricelist(self, pricelist_id, context=None):
        res = super(PurchaseOrder, self).onchange_pricelist(
            pricelist_id)
        if pricelist_id:
            item_obj = self.env['product.pricelist.item']
            for line in self.order_line:
                line.item_id = item_obj.get_best_pricelist_item(
                    pricelist_id, product_id=line.product_id.id,
                    qty=line.product_qty)
        return res

    subtotal_ids = fields.One2many(
        comodel_name='purchase.order.line.subtotal',
        inverse_name='purchase_id', string='Subtotals per line by pricelist')
