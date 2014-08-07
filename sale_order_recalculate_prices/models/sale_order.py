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

from openerp.osv import orm


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    def recalculate_prices(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            pricelist = ''
            if record.pricelist_id.id:
                pricelist = record.pricelist_id.id
            partner = ''
            if record.partner_id.id:
                partner = record.partner_id.id
            date_order = ''
            if record.date_order:
                date_order = record.date_order
            fiscal_position = ''
            if record.fiscal_position.id:
                fiscal_position = record.fiscal_position.id
            if record.order_line:

                for line in record.order_line:
                    res = {}
                    res = line.product_id_change(pricelist,
                                                 line.product_id.id,
                                                 line.product_uom_qty,
                                                 False,
                                                 line.product_uos_qty,
                                                 False,
                                                 line.name, partner,
                                                 False,
                                                 True, date_order,
                                                 False,
                                                 fiscal_position,
                                                 False,
                                                 context=context)
                    vals = {}
                    vals = res['value']
                    line.write(vals, context=context)
        return True
