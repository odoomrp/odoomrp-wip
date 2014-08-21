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
        'typology_id': fields.many2one('sale.order.typology',
                                       'Typology', required=True),
    }

    def on_change_typology_id(self, cr, uid, ids,
                              typology_id, context=context):
        vals = {}
        for order in self.browse(cr, uid, ids, context=context):
            if order.typology_id:
                typology_ids = self.pool['sale.order.typology'].search(
                    cr, uid, [('id', '=', order.typology_id.id)],
                    context=context)
                typology = self.pool['sale.order.typology'].browse(
                    cr, uid, typology_ids, context=context)
                for t in typology:
                    vals['warehouse_id'] = t.warehouse_id.id
                    order.write(vals, context=context)
        return True
