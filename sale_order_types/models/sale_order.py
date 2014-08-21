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


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    _columns = {
        'type_id': fields.many2one('sale.order.type', 'Type', required=True),
    }

    def on_change_type_id(self, cr, uid, ids, type_id, context=None):
        vals = {}
        for order in self.browse(cr, uid, ids, context=context):
            if type_id:
                type_ids = self.pool['sale.order.type'].search(
                    cr, uid, [('id', '=', type_id)], context=context)
                type_obj = self.pool['sale.order.type'].browse(
                    cr, uid, type_ids, context=context)
                for t in type_obj:
                    vals['warehouse_id'] = t.warehouse_id.id
                    order.write(vals, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            type_ids = self.pool['sale.order.type'].search(
                cr, uid, [('id', '=', vals['type_id'])], context=context)
            type_obj = self.pool['sale.order.type'].browse(
                cr, uid, type_ids, context=context)
            if type_obj[0].sequence_id:
                vals['name'] = type_obj[0].sequence_id.get(cr,
                                                           uid, 'sale.order')
            else:
                vals['name'] = self.pool['ir.sequence'].get(cr,
                                                            uid, 'sale.order')
        return super(SaleOrder, self).create(cr, uid, vals, context=context)
