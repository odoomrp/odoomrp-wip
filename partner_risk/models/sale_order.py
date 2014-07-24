
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


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def __init__(self, pool, cr):
            """Add a new state value"""
            super(SaleOrder, self).STATE_SELECTION.append(
                'wait_risk', 'Waiting Risk Approval')
            return super(SaleOrder, self).__init__(pool, cr)

    # Inherited onchange function
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part,
                                                            context)
        partner_obj = self.pool.get['res.partner']
        if part:
            partner = partner_obj.browse(cr, uid, part)
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
