
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com).
#    Copyright (c) 2011 Pexego Sistemas Informáticos.
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
#    Copyright (c) 2014 Factor Libre SL.
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def __init__(self, pool, cr):
            """Add a new state value"""
            super(SaleOrder, self)._columns['state'].selection.append(
                ('wait_risk', 'Waiting Risk Approval'))
            return super(SaleOrder, self).__init__(pool, cr)

    # Inherited onchange function
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part,
                                                            context)
        partner_obj = self.pool['res.partner']
        if part:
            partner = partner_obj.browse(cr, uid, part, context)
            if partner.available_risk < 0.0:
                result['warning'] = {
                    'title': _('Credit Limit Exceeded'),
                    'message': _('Warning: Credit Limit Exceeded.\n\nThis '
                                 'partner has a credit limit of %(limit).2f '
                                 'and already has a debt of %(debt).2f.') % {
                        'limit': partner.credit_limit,
                        'debt': partner.total_debt, }
                }
        return result

    def _amount_invoiced(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for order in self.browse(cr, uid, ids, context):
            if order.invoiced:
                amount = order.amount_total
            else:
                amount = 0.0
                for line in order.order_line:
                    amount += line.amount_invoiced
            result[order.id] = amount
        return result

    _columns = {
        'amount_invoiced': fields.function(_amount_invoiced, method=True,
                                           string='Invoiced Amount',
                                           type='float'),
    }

    def risk_to_router(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        result = {}
        order = self.browse(cr, uid, ids[0])
        partner = order.partner_id
        if partner.comercial_risk_amount > partner.credit_limit:
            raise orm.except_orm(_('Error!'),
                                 _('Warning: Comercial Risk Exceeded.\n'
                                   'Partner has a risk limit of %(risk).2f '
                                   'and already has a debt of %(debt).2f.')
                                 % {'risk': partner.credit_limit,
                                    'debt': partner.comercial_risk_amount})
#            result['warning'] = {
#                'title': _('Financial Risk Exceeded'),
#                'message': _('Warning: Financial Risk Exceeded.\n'
#                             'Partner has a risk limit of %(risk).2f ')
#                                 %{'risk': partner.financial_risk_amount}
#            }
        else:
            from openerp import workflow
            workflow.trg_validate(uid, 'sale.order', ids[0], 'risk_to_router',
                                  cr, context)
        return result


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _amount_invoiced(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for line in self.browse(cr, uid, ids, context):
            # Calculate invoiced amount with taxes included.
            # Note that if a line is only partially invoiced we consider
            # the invoiced amount 0.
            # The problem is we can't easily know if the user changed amounts
            # once the invoice was created
            if line.invoiced:
                result[line.id] = (line.price_subtotal +
                                   self._tax_amount(cr, uid, line))
            else:
                result[line.id] = 0.0
        return result

    def _tax_amount(self, cr, uid, line):
        val = 0.0
        account_tax_obj = self.pool['account.tax']
        for c in account_tax_obj.compute_all(
                cr, uid, line.tax_id,
                line.price_unit * (1-(line.discount or 0.0)/100.0),
                line.product_uom_qty, line.order_id.partner_invoice_id.id,
                line.product_id, line.order_id.partner_id)['taxes']:
            val += c['amount']
        return val

    _columns = {
        'amount_invoiced': fields.function(_amount_invoiced, method=True,
                                           string='Invoiced Amount',
                                           type='float'),
    }
