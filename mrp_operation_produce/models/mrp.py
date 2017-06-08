
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_minor_sequence_operation(self, operations):
        if operations and len(operations) > 1:
            minor_operation = operations[0]
            for operation in operations[1:]:
                if minor_operation.sequence > operation:
                    minor_operation = operation
            return minor_operation
        else:
            return operations and operations[0]

    @api.model
    def _moves_assigned(self):
        res = super(MrpProduction, self)._moves_assigned()
        if res:
            return True
        operation = self._get_minor_sequence_operation(self.workcenter_lines)
        assigned_moves, no_assigned_products = \
            self._get_operation_moves(operation, state='assigned')
        return no_assigned_products == []


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    move_lines = fields.One2many('stock.move', 'work_order',
                                 string='Moves')

    @api.one
    def action_assign(self):
        self.move_lines.action_assign()

    @api.one
    def force_assign(self):
        self.move_lines.force_assign()

    def check_minor_sequence_operations(self):
        seq = self.sequence
        for operation in self.production_id.workcenter_lines:
            if operation.sequence < seq and operation.state != 'done':
                return False
        return True

    def check_operation_moves_state(self, state):
        for move_line in self.move_lines:
            if move_line.state != state:
                return False
        return True

    def action_start_working(self):
        if self.routing_wc_line.previous_operations_finished and \
                not self.check_minor_sequence_operations():
            raise exceptions.Warning(_("Not finished operations"),
                                     _("Previous operations not finished"))
        if not self.check_operation_moves_state('assigned'):
            raise exceptions.Warning(
                _("Missing materials"),
                _("Missing materials to start the production"))
        return super(MrpProductionWorkcenterLine, self).action_start_working()


class MrpRouting(models.Model):

    _inherit = 'mrp.routing'

    previous_operations_finished = fields.Boolean(
        string='Previous operations finished')


class MrpRoutingWorkcenter(models.Model):

    _inherit = 'mrp.routing.workcenter'

    def get_routing_previous_operations(self):
        self.previous_operations_finished = \
            self.routing_id.previous_operations_finished

    previous_operations_finished = fields.Boolean(
        string='Previous operations finished',
        default="get_routing_previous_operations")
