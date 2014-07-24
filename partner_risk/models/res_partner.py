
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com).
#    All Rights Reserved
#    Copyright (c) 2011 Pexego Sistemas Informáticos. All Rights Reserved
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
#    Copyright (c) 2014 Factor Libre SL. All Rights Reserved
#
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
from mx.DateTime import now


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def _unpayed_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        move_line_obj = self.pool['account.move.line']
        today = now().strftime('%Y-%m-%d')
        for partner in self.browse(cr, uid, ids, context):
            accounts = []
            if partner.property_account_receivable:
                accounts.append(partner.property_account_receivable.id)
            if partner.property_account_payable:
                accounts.append(partner.property_account_payable.id)
            line_ids = move_line_obj.search(cr, uid, [
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('reconcile_id', '=', False),
                ('date_maturity', '<', today),
            ], context=context)
            # Those that have amount_to_pay == 0, will mean that they're
            # circulating. The payment request has been sent to the bank but
            # have not yet been reconciled (or the date_maturity has not been
            # reached).
            amount = 0.0
            for line in move_line_obj.browse(cr, uid, line_ids, context):
                # amount += -line.amount_to_pay
                amount += line.debit - line.credit
            res[partner.id] = amount
        return res

    def _circulating_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        move_line_obj = self.pool['account.move.line']
        today = now().strftime('%Y-%m-%d')
        for partner in self.browse(cr, uid, ids, context):
            accounts = []
            if partner.property_account_receivable:
                accounts.append(partner.property_account_receivable.id)
            if partner.property_account_payable:
                accounts.append(partner.property_account_payable.id)
            line_ids = move_line_obj.search(cr, uid, [
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('reconcile_id', '=', False), '|',
                ('date_maturity', '>=', today),
                ('date_maturity', '=', False)
            ], context=context)
            # Those that have amount_to_pay == 0, will mean that they're
            # circulating. The payment request has been sent to the bank but
            # have not yet been reconciled (or the date_maturity has not been
            # reached).
            amount = 0.0
            for line in move_line_obj.browse(cr, uid, line_ids, context):
                # amount += line.debit - line.credit
                amount += line.debit - line.credit + line.amount_to_pay
            res[partner.id] = amount
        return res

    def _pending_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        today = now().strftime('%Y-%m-%d')
        move_line_obj = self.pool['account.move.line']
        for partner in self.browse(cr, uid, ids, context):
            accounts = []
            if partner.property_account_receivable:
                accounts.append(partner.property_account_receivable.id)
            if partner.property_account_payable:
                accounts.append(partner.property_account_payable.id)
            line_ids = move_line_obj.search(cr, uid, [
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('reconcile_id', '=', False),
                '|', ('date_maturity', '>=', today),
                ('date_maturity', '=', False)
            ], context=context)
            # Those that have amount_to_pay == 0, will mean that they're
            # circulating. The payment request has been sent to the bank but
            # have not yet been reconciled (or the date_maturity has not been
            # reached).
            amount = 0.0
            for line in move_line_obj.browse(cr, uid, line_ids, context):
                # amount += line.debit - line.credit
                amount += -line.amount_to_pay
            res[partner.id] = amount
        return res

    def _draft_invoices_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        today = now().strftime('%Y-%m-%d')
        invoice_obj = self.pool['account.invoice']
        for id in ids:
            invids = invoice_obj.search(cr, uid, [('partner_id', '=', id),
                                                  ('state', '=', 'draft'), '|',
                                                  ('date_due', '>=', today),
                                                  ('date_due', '=', False)
                                                  ], context=context)
            val = 0.0
            for invoice in invoice_obj.browse(cr, uid, invids, context):
                # Note that even if the invoice is in 'draft' state it can have
                # an account.move because it may have been validated and
                # brought back to draft. Here we'll only consider invoices with
                # NO account.move as those will be added in other fields.
                if invoice.move_id:
                    continue
                if invoice.type in ('out_invoice', 'in_refund'):
                    val += invoice.amount_total
                else:
                    val -= invoice.amount_total
            res[id] = val
        return res

    def _pending_orders_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        sale_obj = self.pool['sale.order']
        for id in ids:
            sids = sale_obj.search(cr, uid, [
                ('partner_id', '=', id),
                ('state', 'not in', ['draft', 'cancel', 'wait_risk'])
            ], context=context)
            total = 0.0
            for order in sale_obj.browse(cr, uid, sids, context):
                total += order.amount_total - order.amount_invoiced
            res[id] = total
        return res

    def _total_debt(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            pending_orders = partner.pending_orders_amount or 0.0
            circulating = partner.circulating_amount or 0.0
            unpayed = partner.unpayed_amount or 0.0
            pending = partner.pending_amount or 0.0
            draft_invoices = partner.draft_invoices_amount or 0.0
            res[partner.id] = (pending_orders + circulating + unpayed +
                               pending + draft_invoices)
        return res

    def _available_risk(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            res[partner.id] = partner.credit_limit - partner.total_debt
        return res

    def _total_risk_percent(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            if partner.credit_limit:
                res[partner.id] = (100.0 * partner.total_debt /
                                   partner.credit_limit)
            else:
                res[partner.id] = 100
        return res

    _columns = {
        'unpayed_amount': fields.function(_unpayed_amount, method=True,
                                          string=_('Expired Unpaid Payments'),
                                          type='float'),
        'pending_amount': fields.function(
            _pending_amount, method=True,
            string=_('Unexpired Pending Payments'), type='float'),
        'draft_invoices_amount': fields.function(
            _draft_invoices_amount, method=True, string=_('Draft Invoices'),
            type='float'),
        'circulating_amount': fields.function(
            _circulating_amount, method=True,
            string=_('Payments Sent to Bank'), type='float'),
        'pending_orders_amount': fields.function(_pending_orders_amount,
                                                 method=True,
                                                 string=_('Uninvoiced Orders'),
                                                 type='float'),
        'total_debt': fields.function(_total_debt, method=True,
                                      string=_('Total Debt'), type='float'),
        'available_risk': fields.function(_available_risk, method=True,
                                          string=_('Available Credit'),
                                          type='float'),
        'total_risk_percent': fields.function(_total_risk_percent, method=True,
                                              string=_('Credit Usage (%)'),
                                              type='float')
    }
