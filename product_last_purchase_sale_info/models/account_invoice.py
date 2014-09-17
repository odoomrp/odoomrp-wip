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

from openerp.osv import orm


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def action_date_assign(self):
        product_obj = self.pool['product.product']
        res = super(AccountInvoice, self).action_date_assign()
        for o in self:
            ctx = dict(self._context)
            print '*** ctx: ' + str(ctx)
            for line in o.invoice_line:
                if line.product_id and o.type in ('out_invoice', 'in_invoice'):
                    if (o.type == 'out_invoice'):
                        vals = {'last_sale_price': line.price_unit, }
                    elif (o.type == 'in_invoice'):
                        vals = {'last_purchase_price': line.price_unit, }
                    product_obj.write(self.cr, self.uid, [line.product_id.id],
                                      vals, context)
        return True
