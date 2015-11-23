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


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def _get_min_qty_for_production(self, routing=False):
        qty = super(MrpProduction, self)._get_min_qty_for_production(routing)
        min_capacity = routing and max(routing.workcenter_lines.filtered(
            'limited_production_capacity').mapped(
                'workcenter_id.capacity_per_cycle_min') or [0]) or 0
        return max(qty, min_capacity)
