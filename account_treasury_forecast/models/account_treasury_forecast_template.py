# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, _


class AccountTreasuryForecastTemplate(models.Model):
    _name = 'account.treasury.forecast.template'
    _description = 'Treasury Forecast Template'

    name = fields.Char(string="Description", required=True)
    recurring_line_ids = fields.One2many(
        "account.treasury.forecast.line.template", "treasury_template_id",
        string="Recurring Line", domain=[('line_type', '=', 'recurring')])
    variable_line_ids = fields.One2many(
        "account.treasury.forecast.line.template", "treasury_template_id",
        string="Variable Line", domain=[('line_type', '=', 'variable')])


class AccountTreasuryForecastLineTemplate(models.Model):
    _name = 'account.treasury.forecast.line.template'
    _description = 'Treasury Forecast Line Template'

    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Date")
    line_type = fields.Selection([('recurring', 'Recurring'),
                                  ('variable', 'Variable')],
                                 string="Treasury Line Type")
    partner_id = fields.Many2one("res.partner", string="Partner")
    journal_id = fields.Many2one("account.journal", string="Journal",
                                 domain=[("type", "=", "purchase")])
    invoice_id = fields.Many2one("account.invoice", string="Invoice",
                                 domain=[("type", "=", "in_invoice")])
    amount = fields.Float(string="Amount",
                          digits_compute=dp.get_precision('Account'))
    paid = fields.Boolean(string="Invoiced/Paid")
    treasury_template_id = fields.Many2one(
        "account.treasury.forecast.template", string="Treasury Template")

    @api.one
    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.invoice_id:
            self.journal_id = self.invoice_id.journal_id.id
            self.partner_id = self.invoice_id.partner_id.id
            self.amount = self.invoice_id.amount_total
            self.date = self.invoice_id.date_invoice
            self.paid = True

    @api.multi
    def create_invoice(self):
        wiz_obj = self.env['wiz.create.invoice']
        inv_wiz_values = {'partner_id': self.partner_id.id,
                          'journal_id': self.journal_id.id,
                          'description': self.name,
                          'amount': self.amount,
                          'line_id': self.id
                          }
        wiz_id = wiz_obj.create(inv_wiz_values)
        return {'name': _('Create Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.create.invoice',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': wiz_id.id,
                'target': 'new',
                }
