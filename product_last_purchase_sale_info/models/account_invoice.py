# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
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

from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def action_date_assign(self):
        res = super(AccountInvoice, self).action_date_assign()
        for invoice in self:
            for line in invoice.invoice_line:
                if line.product_id:
                    if invoice.type == 'out_invoice':
                        line.product_id.last_sale_price = line.price_unit
                    elif invoice.type == 'in_invoice':
                        line.product_id.last_purchase_price = line.price_unit
        return res
