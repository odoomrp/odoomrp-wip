# -*- encoding: utf-8 -*-
##############################################################################
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recalculate_prices(self):
        for record in self:
            for line in record.order_line:
                if line.product_id:
                    res = line.product_id_change(
                        record.pricelist_id.id, line.product_id.id,
                        line.product_uom_qty, False, line.product_uos_qty,
                        False, line.name, record.partner_id.id, False,
                        True, record.date_order, False,
                        record.fiscal_position.id, False,
                        context=self.env.context)
                    line.write(res['value'])
                #  TODO: Si no tiene product_id debe recalcular el precio según
                #        el template, y tener en cuenta también los atributos
                #        y los valores de estos
        return True
