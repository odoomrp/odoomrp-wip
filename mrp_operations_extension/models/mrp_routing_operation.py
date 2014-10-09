
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 12/09/2014
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

from openerp import models, fields, api


class MrpOperationWorkcenter(models.Model):
    _name = 'mrp.operation.workcenter'
    _description = 'MRP Operation Workcenter'

    workcenter = fields.Many2one('mrp.workcenter', string='Work Center')
    routing_workcenter = fields.Many2one('mrp.routing.workcenter',
                                         'Routing Workcenter')
    time_efficiency = fields.Float('Efficiency Factor')
    capacity_per_cycle = fields.Float('Capacity per Cycle')
    time_cycle = fields.Float('Time for 1 cycle (hour)',
                              help="Time in hours for doing one cycle.")
    time_start = fields.Float('Time before prod.',
                              help="Time in hours for the setup.")
    time_stop = fields.Float('Time after prod.',
                             help="Time in hours for the cleaning.")
    op_number = fields.Integer('Número de Persona', default='0')
    default = fields.Boolean('Default')

    @api.one
    @api.onchange('workcenter')
    def onchange_workcenter(self):
        if self.workcenter:
            self.capacity_per_cycle = self.workcenter.capacity_per_cycle
            self.time_efficiency = self.workcenter.time_efficiency
            self.time_cycle = self.workcenter.time_cycle
            self.time_start = self.workcenter.time_start
            self.time_stop = self.workcenter.time_stop
            self.default = False


class MrpRoutingOperation(models.Model):
    _name = 'mrp.routing.operation'
    _description = 'MRP Routing Operation'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    description = fields.Text('Description')
    steps = fields.Text('Relevant Steps')
    workcenters = fields.Many2many(
        'mrp.workcenter', 'mrp_operation_workcenter_rel', 'operation',
        'workcenter', 'Work centers')
    op_number = fields.Integer('Número de Persona', default='0')
    final_product_to_stock = fields.Boolean(
        string='Move Final Product to Stock')
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type')
