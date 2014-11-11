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


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    workcenter = fields.Many2one('mrp.workcenter', string='Work Center')


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    capacity_per_cycle = fields.Float(
        string='Capacity per Cycle Max.', help='Capacity per cycle maximum.')
    capacity_per_cycle_min = fields.Float(
        string='Capacity per Cycle Min.', help='Capacity per cycle minimum.')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('bom_id', 'bom_id.routing_ids')
    def _compute_permited_routings(self):
        lines = self.env['mrp.routing']
        self.permited_routings = lines
        for routing in self.bom_id.routing_ids:
            lines |= routing
        self.permited_routings = lines

    permited_routings = fields.Many2many(
        'mrp.routing', string='Permited Routings',
        compute='_compute_permited_routings')

    @api.multi
    def product_qty_change_mrp_production(self, product_qty=0,
                                          routing_id=False):
        result = {}
        result['value'] = {}
        routing_obj = self.env['mrp.routing']
        if product_qty and routing_id:
            routing = routing_obj.browse(routing_id)
            if (product_qty < routing.workcenter.capacity_per_cycle_min or
                    product_qty > routing.workcenter.capacity_per_cycle):
                warning = {
                    'title': _('Warning!'),
                    'message': _('Product QTY < Capacity per cycle minimun, or'
                                 ' > Capacity per cycle maximun'),
                }
                result['warning'] = warning
        return result

    @api.one
    @api.onchange('routing_id')
    def onchange_routing(self):
        if self.routing_id:
            self.product_qty = self.routing_id.workcenter.capacity_per_cycle
