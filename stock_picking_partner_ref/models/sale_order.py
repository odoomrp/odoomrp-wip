
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.one
    def action_ship_create(self):

        res = super(SaleOrder, self).action_ship_create()
        for pick in self.picking_ids:
            if self.client_order_ref and \
               self.client_order_ref not in pick.origin:
                pick.origin_partner_ref = '-'.join([pick.origin,
                                                    self.client_order_ref])
        return res
