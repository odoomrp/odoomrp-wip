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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, _
import math


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        routing_id = bom.routing_id.id or routing_id
        result, result2 = super(MrpBom, self)._bom_explode(
            bom, product, factor, properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom)
        result2 = self._get_workorder_operations(
            result2, factor=factor, level=level, routing_id=routing_id)
        return result, result2

    def _get_workorder_operations(self, result2, factor, level=0,
                                  routing_id=False):
        routing_line_obj = self.env['mrp.routing.workcenter']
        for work_order in result2:
            seq = work_order['sequence'] - level
            routing_lines = routing_line_obj.search([
                ('workcenter_id', '=', work_order['workcenter_id']),
                ('sequence', '=', seq)])
            routing_line = routing_lines.filtered(
                lambda x: x.name in work_order['name'])
            cycle = int(math.ceil(factor / routing_line.cycle_nbr))
            hour = routing_line.hour_nbr * cycle
            default_wc_line = routing_line.op_wc_lines.filtered(
                lambda r: r.default)
            work_order['cycle'] = cycle
            work_order['hour'] = hour
            work_order['time_start'] = default_wc_line.time_start
            work_order['time_stop'] = default_wc_line.time_stop
            work_order['routing_wc_line'] = routing_line.id
            work_order['do_production'] = routing_line.do_production
        return result2

    @api.multi
    @api.onchange('routing_id')
    def onchange_routing_id(self):
        for line in self.bom_line_ids:
            line.operation = (self.routing_id.workcenter_lines and
                              self.routing_id.workcenter_lines[0])
        if self.routing_id:
            return {'warning': {
                    'title': _('Changing Routing'),
                    'message': _("Changing routing will cause to change the"
                                 " operation in which each component will be"
                                 " consumed, by default it is set the first"
                                 " one of the routing")
                    }}
        return {}


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    operation = fields.Many2one(
        comodel_name='mrp.routing.workcenter', string='Consumed in')
