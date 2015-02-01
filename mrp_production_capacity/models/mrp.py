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

from openerp import models, fields, api, _
import sys


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    capacity_per_cycle = fields.Float(
        string='Capacity per Cycle Max.', help='Capacity per cycle maximum.')
    capacity_per_cycle_min = fields.Float(
        string='Capacity per Cycle Min.', help='Capacity per cycle minimum.')


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    limited_production_capacity = fields.Boolean()


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def product_qty_change_production_capacity(self, product_qty=0,
                                               routing_id=False):
        result = {}
        routing_obj = self.env['mrp.routing']
        if product_qty and routing_id:
            routing = routing_obj.browse(routing_id)
            for line in routing.workcenter_lines:
                if line.limited_production_capacity:
                    capacity_min = (line.workcenter_id.capacity_per_cycle_min
                                    or sys.float_info.min)
                    capacity_max = (line.workcenter_id.capacity_per_cycle or
                                    sys.float_info.max)
                    if capacity_min and capacity_max:
                        if (product_qty < capacity_min or
                                product_qty > capacity_max):
                            warning = {
                                'title': _('Warning!'),
                                'message': _('Product QTY < Capacity per cycle'
                                             ' minimun, or > Capacity per'
                                             ' cycle maximun')
                            }
                            result['warning'] = warning
        return result

    @api.one
    @api.onchange('routing_id')
    def onchange_routing(self):
        if self.routing_id:
            for line in self.routing_id.workcenter_lines:
                if (line.limited_production_capacity and
                        line.workcenter_id.capacity_per_cycle):
                    self.product_qty = line.workcenter_id.capacity_per_cycle


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    def workcenter_change_production_capacity(self, product_qty=0,
                                              workcenter_id=False):
        result = {}
        result['value'] = {}
        workcenter_obj = self.env['mrp.workcenter']
        if product_qty and workcenter_id:
            workcenter = workcenter_obj.browse(workcenter_id)
            capacity_min = (workcenter.capacity_per_cycle_min or
                            sys.float_info.min)
            capacity_max = (workcenter.capacity_per_cycle or
                            sys.float_info.max)
            if capacity_min and capacity_max:
                if (product_qty < capacity_min or
                        product_qty > capacity_max):
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Product QTY < Capacity per cycle'
                                     ' minimun, or > Capacity per'
                                     ' cycle maximun')
                    }
                    result['warning'] = warning
        return result
