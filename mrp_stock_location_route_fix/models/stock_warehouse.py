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

from openerp import models, exceptions, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def _get_manufacture_pull_rule(self, cr, uid, warehouse, context=None):
        route_obj = self.pool['stock.location.route']
        data_obj = self.pool['ir.model.data']
        try:
            manufacture_route_id = data_obj.get_object_reference(
                cr, uid, 'mrp', 'route_warehouse0_manufacture')[1]
        except:
            manufacture_route_id = route_obj.search(
                cr, uid, [('name', 'like', 'Manufacture')], context=context)
            manufacture_route_id = (manufacture_route_id and
                                    manufacture_route_id[0] or False)
        if not manufacture_route_id:
            raise exceptions.except_orm(
                _('Error!'), _('Can\'t find any generic Manufacture route.'))
        return {
            'name': self._format_routename(cr, uid, warehouse,
                                           _(' Manufacture'), context=context),
            'location_id': warehouse.lot_stock_id.id,
            'route_id': manufacture_route_id,
            'action': 'manufacture',
            'picking_type_id': warehouse.int_type_id.id,
            'propagate': False, 
            'warehouse_id': warehouse.id,
        }
