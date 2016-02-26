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
from openerp.osv import fields as old_fields
import openerp.addons.decimal_precision as dp
from lxml import etree


class SaleOrderLineSubtotal(models.Model):
    _name = 'sale.order.line.subtotal'

    @api.one
    def _calculate_subtotal(self):
        price = (self.line_id.price_unit *
                 (1 - (self.item_id.discount or 0.0) / 100) *
                 (1 - (self.item_id.discount2 or 0.0) / 100) *
                 (1 - (self.item_id.discount3 or 0.0) / 100))
        qty = self.line_id.product_uom_qty
        if self.item_id.offer_id:
            total = (self.item_id.offer_id.free_qty +
                     self.item_id.offer_id.paid_qty)
            qty = round((qty / total) * self.item_id.offer_id.paid_qty)
        taxes = self.line_id.tax_id.compute_all(
            price, qty, self.line_id.product_id, self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        self.subtotal = cur.round(taxes['total'])

    line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Line', ondelete='cascade')
    sale_id = fields.Many2one(
        comodel_name='sale.order', string='Sale Order',
        related='line_id.order_id', store=True)
    item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string='Pricelist Item',
        ondelete='cascade')
    subtotal = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        compute='_calculate_subtotal')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _calc_price_subtotal(self):
        self.ensure_one()
        price = (self.price_unit *
                 (1 - (self.discount or 0.0) / 100.0) *
                 (1 - (self.discount2 or 0.0) / 100.0) *
                 (1 - (self.discount3 or 0.0) / 100.0))
        return price

    @api.multi
    def _calc_qty(self):
        self.ensure_one()
        qty = self.product_uom_qty
        if self.offer_id:
            total = self.offer_id.free_qty + self.offer_id.paid_qty
            packs = qty // total
            remaining = qty - packs * total
            if remaining:
                if remaining < self.offer_id.paid_qty:
                    qty = packs * self.offer_id.paid_qty + remaining
                else:
                    qty = (packs + 1) * self.offer_id.paid_qty
            else:
                qty = packs * self.offer_id.paid_qty
        return qty

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            new_price_subtotal = self._calc_price_subtotal(cr, uid, line.id,
                                                           context=context)
            qty = self._calc_qty(cr, uid, line.id, context=context)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id,
                                        new_price_subtotal, qty,
                                        line.product_id,
                                        line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    def _get_possible_item_ids(self, pricelist_id, product_id=False, qty=0):
        item_obj = self.env['product.pricelist.item']
        item_ids = item_obj.domain_by_pricelist(
            pricelist_id, product_id=product_id, qty=qty)
        return item_ids

    @api.one
    @api.depends('product_id', 'product_uom_qty',
                 'order_id.pricelist_id')
    def _get_possible_items(self):
        item_ids = self._get_possible_item_ids(
            self.order_id.pricelist_id.id, product_id=self.product_id.id,
            qty=self.product_uom_qty)
        self.possible_item_ids = [(6, 0, item_ids)]

    discount2 = fields.Float(
        string='Disc. 2 (%)', digits=dp.get_precision('Discount'),
        readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    discount3 = fields.Float(
        string='Disc. 3 (%)', digits=dp.get_precision('Discount'),
        readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    offer_id = fields.Many2one(
        comodel_name='product.pricelist.item.offer', string='Offer')
    item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string='Pricelist Item')
    possible_item_ids = fields.Many2many(
        comodel_name='product.pricelist.item',
        compute='_get_possible_items')
    subtotal_ids = fields.One2many(
        comodel_name='sale.order.line.subtotal', inverse_name='line_id',
        string='Subtotals by pricelist')

    _columns = {
        'price_subtotal': old_fields.function(
            _amount_line, type="float", string='Subtotal',
            digits_compute=dp.get_precision('Account'))
    }

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         _('Second discount must be lower than 100%.')),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         _('Third discount must be lower than 100%.')),
    ]

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(SaleOrderLine, self).default_get(cr, uid, fields_list,
                                                     context=context)
        item_obj = self.pool['product.pricelist.item']
        if context.get('pricelist_id'):
            item_id = item_obj.get_best_pricelist_item(
                cr, uid, context['pricelist_id'], context=context)
            res.update({'item_id': item_id})
        return res

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
            name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        warning_msgs = res.get('warning') and res['warning']['message'] or ''
        item_obj = self.env['product.pricelist.item']
        if product:
            item_id = item_obj.get_best_pricelist_item(
                pricelist, product_id=product, qty=qty, partner_id=partner_id)
            if not item_id:
                warn_msg = _('Cannot find a pricelist line matching this '
                             'product and quantity.\nYou have to change either'
                             ' the product, the quantity or the pricelist.')
                warning_msgs += (_("No valid pricelist line found ! :") +
                                 warn_msg + "\n\n")
            else:
                res['value']['price_unit'] = item_obj.browse(
                    item_id).price_get(product, qty, partner_id, uom)[0]
                res['value'].update({'item_id': item_id})
                res['domain'].update({'item_id':
                                      [('id', 'in',
                                        self._get_possible_item_ids(
                                            pricelist, product_id=product,
                                            qty=qty))]})
        if warning_msgs:
            res['warning'] = {'title': _('Configuration Error!'),
                              'message': warning_msgs}
        return res

    @api.onchange('item_id')
    def onchange_item_id(self):
        if self.item_id:
            self.discount = self.item_id.discount
            self.discount2 = self.item_id.discount2
            self.discount3 = self.item_id.discount3
            self.offer_id = self.item_id.offer
            if not self.offer_id and self.item_id.base == -1:
                item_obj = self.env['product.pricelist.item']
                item_ids = item_obj.domain_by_pricelist(
                    self.item_id.base_pricelist_id.id,
                    product_id=self.product_id.id, qty=self.product_uom_qty,
                    partner_id=self.order_id.partner_id.id)
                for item in item_obj.browse(item_ids):
                    if item.offer:
                        self.offer_id = item.offer
                        break
            if self.product_id:
                self.price_unit = self.item_id.price_get(
                    self.product_id.id, self.product_uom_qty,
                    self.order_id.partner_id.id, self.product_id.uom_id.id)[0]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
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
        for c in line.tax_id.compute_all(new_price_subtotal,
                                         qty, line.product_id,
                                         line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    @api.multi
    def onchange_pricelist_id(self, pricelist_id, order_lines, context=None):
        res = super(SaleOrder, self).onchange_pricelist_id(
            pricelist_id, order_lines)
        if pricelist_id:
            item_obj = self.env['product.pricelist.item']
            for line in self.order_line:
                line.item_id = item_obj.get_best_pricelist_item(
                    pricelist_id, product_id=line.product_id.id,
                    qty=line.product_uom_qty,
                    partner_id=line.order_id.partner_id.id)
        return res

    subtotal_ids = fields.One2many(
        comodel_name='sale.order.line.subtotal', inverse_name='sale_id',
        string='Subtotals per line by pricelist')
