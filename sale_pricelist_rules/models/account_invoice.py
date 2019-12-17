# -*- coding: utf-8 -*-
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    discount2 = fields.Float(
        string='Disc. 2 (%)', digits=dp.get_precision('Discount'),
        default=0.0)
    discount3 = fields.Float(
        string='Disc. 3 (%)', digits=dp.get_precision('Discount'),
        default=0.0)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'discount2', 'discount3',
                 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = (self.price_unit *
                 (1 - (self.discount or 0.0) / 100.0) *
                 (1 - (self.discount2 or 0.0) / 100.0) *
                 (1 - (self.discount3 or 0.0) / 100.0))
        taxes = self.invoice_line_tax_id.compute_all(
            price, self.quantity, product=self.product_id,
            partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(
                self.price_subtotal)


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(
            date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            price = (line.price_unit *
                     (1 - (line.discount or 0.0) / 100.0) *
                     (1 - (line.discount2 or 0.0) / 100.0) *
                     (1 - (line.discount3 or 0.0) / 100.0))
            taxes = line.invoice_line_tax_id.compute_all(
                price, line.quantity, line.product_id,
                invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(
                        tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice', 'in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(
                        val['base'] * tax['base_sign'], company_currency,
                        round=False)
                    val['tax_amount'] = currency.compute(
                        val['amount'] * tax['tax_sign'], company_currency,
                        round=False)
                    val['account_id'] = (
                        tax['account_collected_id'] or line.account_id.id)
                    val['account_analytic_id'] = (
                        tax['account_analytic_collected_id'])
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(
                        val['base'] * tax['ref_base_sign'], company_currency,
                        round=False)
                    val['tax_amount'] = currency.compute(
                        val['amount'] * tax['ref_tax_sign'], company_currency,
                        round=False)
                    val['account_id'] = (
                        tax['account_paid_id'] or line.account_id.id)
                    val['account_analytic_id'] = (
                        tax['account_analytic_paid_id'])
                # If the taxes generate moves on the same financial account as
                # the invoice line and no default analytic account is defined
                # at the tax level, propagate the analytic account from the
                # invoice line to the tax line. This is necessary in situations
                # were (part of) the taxes cannot be reclaimed, to ensure the
                # tax move is allocated to the proper analytic account.
                if (not val.get('account_analytic_id') and
                        line.account_analytic_id and
                        val['account_id'] == line.account_id.id):
                    val['account_analytic_id'] = line.account_analytic_id.id
                key = (val['tax_code_id'], val['base_code_id'],
                       val['account_id'])
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']
        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])
        return tax_grouped
