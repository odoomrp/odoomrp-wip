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
from openerp import models, fields, api


class WizCreateInvoice(models.TransientModel):
    _name = 'wiz.create.invoice'
    _description = 'Wizard to create invoices'

    partner_id = fields.Many2one("res.partner", string="Partner")
    journal_id = fields.Many2one("account.journal", string="Journal",
                                 domain=[("type", "=", "purchase")])
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount",
                          digits_compute=dp.get_precision('Account'))
    line_id = fields.Many2one("account.treasury.forecast.line.template",
                              string="Payment")

    @api.one
    def button_create_inv(self):
        invoice_obj = self.env['account.invoice']
        res_inv = invoice_obj.onchange_partner_id('in_invoice',
                                                  self.partner_id.id)
        values = res_inv['value']
        values['name'] = ('Treasury: ' + self.description + '/ Amount: ' +
                          str(self.amount))
        values['reference'] = ('Treasury: ' + self.description + '/ Amount: ' +
                               str(self.amount))
        values['partner_id'] = self.partner_id.id
        values['journal_id'] = self.journal_id.id
        values['type'] = 'in_invoice'
        invoice_id = invoice_obj.create(values)
        self.line_id.write({'invoice_id': invoice_id.id, 'paid': 1,
                            'journal_id': self.journal_id.id,
                            'partner_id': self.partner_id.id,
                            'amount': self.amount})
        return {'type': 'ir.actions.act_window_close'}
