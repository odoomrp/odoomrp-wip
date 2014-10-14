
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com).
#    Copyright (c) 2011 Pexego Sistemas Informáticos.
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

from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('acc_move_lines.debit', 'acc_move_lines.credit')
    def _unpayed_amount(self):
        move_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        today = fields.date.today()
        for partner in self:
            account_lst = account_obj.search(['|', ('type', '=', 'receivable'),
                                              ('type', '=', 'payable')]).ids
            line_ids = move_line_obj.search([('partner_id', '=', partner.id),
                                             ('account_id', 'in', account_lst),
                                             ('reconcile_id', '=', False),
                                             ('date_maturity', '<', today)])
            # Those that have amount_residual == 0, will mean that they're
            # circulating. The payment request has been sent to the bank but
            # have not yet been reconciled (or the date_maturity has not been
            # reached).
            amount = 0.0
            for line in line_ids:
                # amount += -line.amount_to_pay
                amount += line.debit - line.credit
            partner.unpayed_amount = amount

    @api.multi
    @api.depends('acc_move_lines.debit', 'acc_move_lines.credit',
                 'acc_move_lines.amount_residual')
    def _circulating_amount(self):
        today = fields.date.today()
        move_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        for partner in self:
            account_lst = account_obj.search(['|', ('type', '=', 'receivable'),
                                             ('type', '=', 'payable')]).ids
            line_ids = move_line_obj.search([('partner_id', '=', partner.id),
                                             ('account_id', 'in', account_lst),
                                             ('reconcile_id', '=', False), '|',
                                             ('date_maturity', '>=', today),
                                             ('date_maturity', '=', False)])
            # Those that have amount_residual == 0, will mean that they're
            # circulating. The payment request has been sent to the bank but
            # have not yet been reconciled (or the date_maturity has not been
            # reached).
            amount = 0.0
            for line in line_ids:
                # amount += line.debit - line.credit
                amount += line.debit - line.credit + line.amount_residual
            partner.circulating_amount = amount

    @api.multi
    @api.depends('acc_move_lines.amount_residual')
    def _pending_amount(self):
        today = fields.date.today()
        move_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        for partner in self:
            account_lst = account_obj.search(['|', ('type', '=', 'receivable'),
                                              ('type', '=', 'payable')]).ids
            line_ids = move_line_obj.search([('partner_id', '=', partner.id),
                                             ('account_id', 'in', account_lst),
                                             ('reconcile_id', '=', False), '|',
                                             ('date_maturity', '>=', today),
                                             ('date_maturity', '=', False)])
            # Those that have amount_to_pay == 0, will mean that they're
            # circulating. The payment request has been sent to the bank but
            # have not yet been reconciled (or the date_maturity has not been
            # reached).
            amount = 0.0
            for line in line_ids:
                # amount += line.debit - line.credit
                amount += -line.amount_residual
            partner.pending_amount = amount

    @api.multi
    @api.depends('invoice_ids.amount_total')
    def _draft_invoices_amount(self):
        today = fields.date.today()
        invoice_obj = self.env['account.invoice']
        for partner in self:
            invids = invoice_obj.search([('partner_id', '=', partner.id),
                                         ('state', '=', 'draft'), '|',
                                         ('date_due', '>=', today),
                                         ('date_due', '=', False)])
            val = 0.0
            for invoice in invids:
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
            partner.draft_invoices_amount = val

    @api.multi
    @api.depends('sale_order_ids.amount_total',
                 'sale_order_ids.amount_invoiced')
    def _pending_orders_amount(self):
        for partner in self:
            sale_obj = self.env['sale.order']
            sids = sale_obj.search([('partner_id', '=', partner.id),
                                    ('state', 'not in',
                                     ['draft', 'cancel', 'wait_risk'])])
            total = 0.0
            for order in sids:
                total += order.amount_total - order.amount_invoiced
            partner.pending_orders_amount = total

    @api.multi
    @api.depends('unpayed_amount', 'pending_amount', 'circulating_amount',
                 'pending_orders_amount')
    def _total_debt(self):
        for partner in self:
            pending_orders = partner.pending_orders_amount or 0.0
            circulating = partner.circulating_amount or 0.0
            unpayed = partner.unpayed_amount or 0.0
            pending = partner.pending_amount or 0.0
            draft_invoices = partner.draft_invoices_amount or 0.0
            partner.total_debt = (pending_orders + circulating + unpayed +
                                  pending + draft_invoices)

    @api.one
    @api.depends('total_debt', 'credit_limit')
    def _available_risk(self):
        self.available_risk = self.credit_limit - self.total_debt

    @api.one
    @api.depends('total_debt', 'credit_limit')
    def _total_risk_percent(self):
        if self.credit_limit:
            self.total_risk_percent = (100.0 * self.total_debt /
                                       self.credit_limit)
        else:
            self.total_risk_percent = 100

    @api.multi
    @api.depends('invoice_ids.residual', 'stock_move_lines.price_unit',
                 'stock_move_lines.product_qty')
    def _fc_risk_amount(self):
        for partner in self:
            invoice_obj = self.env['account.invoice']
            stpick_obj = self.env['stock.picking']
            stpick_type_obj = self.env['stock.picking.type']
            stock_move_obj = self.env['stock.move']
            delivery = stpick_type_obj.search([('name', '=',
                                                _('Delivery Orders'))])[0]
            # check invoices residual
            invids = invoice_obj.search(
                [('partner_id', '=', partner.id), ('state', '=', 'open'),
                 ('residual', '>', 0),
                 ('type', 'in', ('out_invoice', 'out_refund'))])
            residual_total = 0.0
            total_undelibered = 0.0
            for invoice in invids:
                residual_total += invoice.residual
            total_undelibered = residual_total
            # check stock_pickings
            stpick_lst = stpick_obj.search([('invoice_state', 'in',
                                             ('none', '2binvoiced')),
                                            ('picking_type_id', '=',
                                             delivery.id),
                                            ('state', '!=', 'cancel')])
            for stock in stpick_lst:
                move_lst = stock_move_obj.search([('picking_id', '=',
                                                   stock.id)])
                stpick_amount = 0.0
                stpick_undelibered_amount = 0.0
                undelibered_amount = 0.0
                for move in move_lst:
                    # compute only delivered lines
                    # TODO PRICE UNIT in move not updated - Odoo bug?
                    if move.state == 'done':
                        line_amount = move.price_unit * move.product_qty
                        stpick_amount += line_amount
                    else:
                        undelibered_amount = move.price_unit * move.product_qty
                        stpick_undelibered_amount += undelibered_amount
                residual_total += stpick_amount
                total_undelibered += stpick_amount + stpick_undelibered_amount
            partner.write({'financial_risk_amount': residual_total,
                           'comercial_risk_amount': total_undelibered})

    def action_open_risk_window(self, cr, uid, ids, context=None):
        data_obj = self.pool['ir.model.data']
        id2 = data_obj._get_id(cr, uid, 'partner_risk',
                               'open_risk_window_view')
        if id2:
            id2 = data_obj.browse(cr, uid, id2, context=context).res_id
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'views': [(id2, 'form')],
            'view_id': False,
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
            }

    unpayed_amount = fields.Float(string=_('Expired Unpaid Payments'),
                                  compute=_unpayed_amount)
    pending_amount = fields.Float(string=_('Unexpired Pending Payments'),
                                  compute=_pending_amount)
    draft_invoices_amount = fields.Float(string=_('Draft Invoices'),
                                         compute=_draft_invoices_amount)
    circulating_amount = fields.Float(string=_('Payments Sent to Bank'),
                                      compute=_circulating_amount)
    pending_orders_amount = fields.Float(string=_('Uninvoiced Orders'),
                                         compute=_pending_orders_amount)
    financial_risk_amount = fields.Float(string=_('Financial Risk'),
                                         compute=_fc_risk_amount)
    comercial_risk_amount = fields.Float(string=_('Comercial Risk'),
                                         compute=_fc_risk_amount)
    total_debt = fields.Float(string=_('Total Debt'), compute=_total_debt)
    available_risk = fields.Float(string=_('Available Credit'),
                                  compute=_available_risk)
    total_risk_percent = fields.Float(string=_('Credit Usage (%)'),
                                      compute=_total_risk_percent)
    acc_move_lines = fields.One2many('account.move.line', 'partner_id',
                                     'Account Move lines')
    stock_move_lines = fields.One2many('stock.move', 'partner_id',
                                       'Stock Move lines')
