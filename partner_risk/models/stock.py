
# -*- encoding: utf-8 -*-
##############################################################################
#
#    AvanzOSC (Daniel).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        for move in self:
            partner = move.partner_id
            frisk = partner.financial_risk_amount
            limit = partner.credit
            res = super(StockMove, self).action_done()
            if frisk > limit:
                res['warning'] = {
                    'title': _('Credit Limit Exceeded'),
                    'message': _('Warning: Financial Risk Exceeded.\n Partner'
                                 'has a risk limit of %(risk).2f and already '
                                 'has a debt of %(debt).2f.'
                                 ) % {'risk': partner.credit_limit,
                                      'debt': partner.financial_risk_amount}}
            return res
