
# -*- encoding: utf-8 -*-
##############################################################################
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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def __init__(self, pool, cr):
        """Add a new state value"""
        if not (('wait_risk', 'Waiting Risk Approval')) in (
                self._columns['state'].selection):
            i = self._columns['state'].selection.index(
                ('draft', 'Draft Quotation'))
            super(SaleOrder, self)._columns['state'].selection.insert(
                i+1, ('wait_risk', 'Waiting Risk Approval'))
        super(SaleOrder, self).__init__(pool, cr)

    amount_invoiced = fields.Float(string='Invoiced Amount',
                                   compute="_amount_invoiced")

    # Inherited onchange function
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part,
                                                            context)
        partner_obj = self.pool['res.partner']
        if part:
            partner = partner_obj.browse(cr, uid, part, context)
            if partner.available_risk < 0.0:
                result['warning'] = {
                    'title': _('Credit Limit Exceeded'),
                    'message': _('Warning: Credit Limit Exceeded.\n\nThis '
                                 'partner has a credit limit of %(limit).2f '
                                 'and already has a debt of %(debt).2f.') % {
                        'limit': partner.credit_limit,
                        'debt': partner.total_debt}}
            elif partner.comercial_risk_amount > partner.credit_limit:
                result['warning'] = {
                    'title': _('Comercial Risk Exceeded'),
                    'message': _('Warning: Comercial Risk Exceeded.\n\nThis '
                                 'partner has a risk limit of %(limit).2f '
                                 'and already has a debt of %(debt).2f.') % {
                        'limit': partner.credit_limit,
                        'debt': partner.comercial_risk_amount}}
            elif partner.financial_risk_amount > partner.credit_limit:
                result['warning'] = {
                    'title': _('Financial Risk Exceeded'),
                    'message': _('Warning: Comercial Risk Exceeded.\n\nThis '
                                 'partner has a risk limit of %(limit).2f '
                                 'and already has a debt of %(debt).2f.') % {
                        'limit': partner.credit_limit,
                        'debt': partner.financial_risk_amount}}
            else:
                return result

        return result

    @api.multi
    @api.depends('amount_invoiced')
    def _amount_invoiced(self):
        for sale_order in self:
            if sale_order.invoiced:
                amount = self.amount_total
            else:
                amount = 0.0
            for line in sale_order.order_line:
                amount += line.amount_invoiced
            sale_order.amount_invoiced = amount


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('amount_invoiced')
    def _amount_invoiced(self):
        # Calculate invoiced amount with taxes included.
        # Note that if a line is only partially invoiced we consider
        # the invoiced amount 0.
        # The problem is we can't easily know if the user changed amounts
        # once the invoice was created
        for sale_line in self:
            if sale_line.invoiced:
                amount = sale_line.price_subtotal + sale_line._tax_amount()
            else:
                amount = 0.0
            sale_line.amount_invoiced = amount

    def _tax_amount(self):
        val = 0.0
        account_tax_obj = self.env['account.tax']
        for c in account_tax_obj.compute_all(
                self.price_unit * (1-(self.discount or 0.0)/100.0),
                self.product_uom_qty, self.order_id.partner_invoice_id.id,
                self.product_id, self.order_id.partner_id)['taxes']:
            val += c['amount']
        return val

    amount_invoiced = fields.Float(string='Invoiced Amount',
                                   compute="_amount_invoiced")
