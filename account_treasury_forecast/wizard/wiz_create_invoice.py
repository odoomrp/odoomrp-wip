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

import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, exceptions, _


class WizCreateInvoice(models.TransientModel):
    _name = 'wiz.create.invoice'
    _description = 'Wizard to create invoices'

    partner_id = fields.Many2one("res.partner", string="Partner")
    journal_id = fields.Many2one("account.journal", string="Journal",
                                 domain=[("type", "=", "purchase")])
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount",
                          digits_compute=dp.get_precision('Account'))
    payment = fields.Integer(string="Payment")
    type = fields.Char(string="Type")

    @api.one
    def button_create_inv(self):
        invoice_obj = self.env['account.invoice']
        values = {'name': 'Treasury: ' + self.description + '/ Amount: ' +
                  str(self.amount),
                  'reference': 'Treasury: ' + self.description + '/ Amount: ' +
                  str(self.amount),
                  'partner_id': self.partner_id.id,
                  'journal_id': self.journal_id.id,
                  'type': 'in_invoice',
#                  'account_id': self.partner_id.property_account_payable.id,
#                  'payment_term': self.partner_id.property_payment_term.id,
#                  'fiscal_position':
#                      self.partner_id.property_account_position.id
                  }
        print values
        invoice_id = invoice_obj.create(values)
        if self.type == 'V':
            obj = self.env['account.treasury.forecast.variable.template']
        else:
            obj = self.env['account.treasury.forecast.recurring.template']
        pay_o = obj.browse(self.payment)
        pay_o.write({'factura_id': invoice_id, 'paid': 1, 'journal_id':
                     self.journal_id.id})
        return {'type': 'ir.actions.act_window_close'}
