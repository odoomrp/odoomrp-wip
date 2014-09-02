# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from openerp import api, models

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    @api.one
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        if self.origin:
            orders = self.env['sale.order'].seach(
                [('name', '=', self.origin)])
            journal_id = orders[0].type_id.journal_id.id
        return super(AccountInvoice, self)._prepare_refund(
            self, invoice, date, period_id, description, journal_id)
