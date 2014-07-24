
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
