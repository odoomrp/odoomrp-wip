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

from openerp import models, api
import math


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _action_compute_lines_variants(self, properties=None):
        results = super(MrpProduction, self)._action_compute_lines_variants(
            properties=properties)
        self._compute_planned_workcenter()
        self._get_workorder_in_product_lines(self.workcenter_lines,
                                             self.product_lines,
                                             properties=properties)
        return results

    def _get_workorder_in_product_lines(self, workcenter_lines, product_lines,
                                        properties=None):
        for workorder in workcenter_lines:
            wc = workorder.routing_wc_line
            cycle = wc.cycle_nbr and int(math.ceil(self.product_qty /
                                                   wc.cycle_nbr)) or 0
            workorder.cycle = cycle
            workorder.hour = wc.hour_nbr * cycle
        for p_line in product_lines:
            self._set_workorder(self.bom_id, p_line, workcenter_lines,
                                properties=properties)

    def _set_workorder(self, bom, p_line, workcenter_lines, properties=None):
        phantom_op = self.env.context.get('phantom_op', False)
        for bom_line in bom.bom_line_ids:
            if ((bom_line.product_template.id == p_line.product_template.id or
                    bom_line.product_id.product_tmpl_id.id ==
                    p_line.product_template.id) and
                    (not bom_line.product_id or
                     bom_line.product_id.id == p_line.product_id.id)):
                for wc_line in workcenter_lines:
                    if wc_line.routing_wc_line == (phantom_op or
                                                   bom_line.operation):
                        p_line.work_order = wc_line
                        break
                continue
            elif bom_line.type == 'phantom':
                bom_obj = self.env['mrp.bom']
                if not bom_line.product_id:
                    bom_id = bom_obj._bom_find(
                        product_tmpl_id=bom_line.product_template.id,
                        properties=properties)
                else:
                    bom_id = bom_obj._bom_find(
                        product_id=bom_line.product_id.id,
                        properties=properties)
                if not phantom_op:
                    phantom_op = bom_line.operation
                self.with_context(phantom_op=phantom_op)._set_workorder(
                    bom_obj.browse(bom_id), p_line,  workcenter_lines,
                    properties=properties)
