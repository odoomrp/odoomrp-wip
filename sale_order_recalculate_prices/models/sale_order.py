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

from openerp.osv import fields, orm
# from openerp.tools.translate import _


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    def recalculate_prices(self, cr, uid, ids, context=None):
        records = self.browse(cr, uid, ids, context=context)
        pricelist = ''
        if records[0].pricelist_id.id:
            pricelist = records[0].pricelist_id.id
        partner = ''
        if records[0].partner_id.id:
            partner = records[0].partner_id.id
        date_order = ''
        if records[0].date_order:
            date_order = records[0].date_order
        fiscal_position = ''
        if records[0].fiscal_position.id:
            fiscal_position = records[0].fiscal_position.id
        if records[0].order_line:
            for line in records[0].order_line:
                res = {}
                res = line.product_id_change(pricelist, line.product_id.id,
                                             line.product_uom_qty, False,
                                             line.product_uos_qty, False,
                                             line.name, partner, False,
                                             True, date_order, False,
                                             fiscal_position, False,
                                             context=context)
                vals = {}
                vals = res['value']
                # raise orm.except_orm(_('LOL'), _("%s") % vals)
                line.write(cr, uid, line.id, vals, context=context)
        return True
