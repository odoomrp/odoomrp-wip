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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class SaleOrderTax(models.Model):
    _name = 'sale.order.tax_breakdown'

    sale_order = fields.Many2one('sale.order', string='Sale Order',
                                 ondelete='cascade')
    tax = fields.Many2one('account.tax', string='Tax')
    untaxed_amount = fields.Float(string='Untaxed Amount',
                                  digits=dp.get_precision('Sale Price'))
    taxation_amount = fields.Float(string='Taxation',
                                   digits=dp.get_precision('Sale Price'))
    total_amount = fields.Float(string='Total',
                                digits=dp.get_precision('Sale Price'))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    taxes = fields.One2many('sale.order.tax_breakdown', 'sale_order',
                            string='Tax Breakdown')

    @api.multi
    def _calc_breakdown_taxes(self):
        apport_obj = self.pool['sale.order.tax_breakdown']
        cur_obj = self.pool['res.currency']
        for order in self:
            order.write({'taxes': [(6, 0, [])]})
            for line in order.order_line:
                cur = line.order_id.pricelist_id.currency_id
                for tax in line.tax_id:
                    apport_ids = apport_obj.search(self.env.cr, self.env.uid,
                                                   [('sale_order', '=', order.id),
                                                    ('tax', '=', tax.id)],
                                                   context=self.env.context)
                    if not apport_ids:
                        line_vals = {
                            'sale_order': order.id,
                            'tax': tax.id,
                            'untaxed_amount':
                            cur_obj.round(self.env.cr, self.env.uid, cur,
                                          line.price_subtotal),
                            'taxation_amount':
                            cur_obj.round(self.env.cr, self.env.uid, cur,
                                          (line.price_subtotal * tax.amount)),
                            'total_amount':
                            cur_obj.round(self.env.cr, self.env.uid, cur,
                                          (line.price_subtotal *
                                           (1 + tax.amount)))
                        }
                        apport_obj.create(self.env.cr, self.env.uid, line_vals)
                    else:
                        apport = apport_obj.browse(self.env.cr, self.env.uid,
                                                   apport_ids[0])
                        untaxed_amount = cur_obj.round(
                            self.env.cr, self.env.uid, cur,
                            line.price_subtotal + apport.untaxed_amount)
                        taxation_amount = cur_obj.round(
                            self.env.cr, self.env.uid, cur,
                            untaxed_amount * tax.amount)
                        total_amount = cur_obj.round(
                            self.env.cr, self.env.uid, cur,
                            untaxed_amount + taxation_amount)
                        apport_obj.write(self.env.cr, self.env.uid,
                                         [apport.id],
                                         {'untaxed_amount': untaxed_amount,
                                          'taxation_amount': taxation_amount,
                                          'total_amount': total_amount})
        return True

    def action_wait(self, cr, uid, ids, context=None):
        self._calc_breakdown_taxes(cr, uid, ids, context=context)
        return super(SaleOrder, self).action_wait(cr, uid, ids, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        super(SaleOrder, self).button_dummy(cr, uid, ids, context=context)
        if ids:
            self._calc_breakdown_taxes(cr, uid, ids, context=context)
        return True
