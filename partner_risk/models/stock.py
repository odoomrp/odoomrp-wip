
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

from openerp.osv import orm
from openerp.tools.translate import _


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):
        st_move = self.browse(cr, uid, ids[0])
        partner = st_move.partner_id
        warning = self.pool['warning']
        if partner.financial_risk_amount > partner.credit_limit:
            # return orm.except_orm(_('Error!'),
            #                     _('Warning: Financial Risk Exceeded.\n'
            #                       'Partner has a risk limit of %(risk).2f '
            #                       'and already has a debt of %(debt).2f.')
            #                     % {'risk': partner.credit_limit,
            #                        'debt': partner.financial_risk_amount})
            info = {'title': 'Warning',
                    'message': _('Warning: Financial Risk Exceeded.\n'
                                 'Partner has a risk limit of %(risk).2f '
                                 'and already has a debt of %(debt).2f.')
                    % {'risk': partner.credit_limit,
                       'debt': partner.financial_risk_amount}}
            # TODO - Barcode Interfaze view
            # Info or Block?
            # res = super(StockMove, self).action_done(cr, uid, ids,
            #             context=context)
            return warning.warning(cr, uid, title=info['title'],
                                   message=info['message'])
        else:
            kk
            return super(StockMove, self).action_done(cr, uid, ids,
                                                      context=context)
