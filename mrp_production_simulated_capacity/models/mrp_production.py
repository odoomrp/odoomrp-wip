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
import sys


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def _get_min_qty_for_production(self, routing=False):
        qty = super(MrpProduction, self)._get_min_qty_for_production(routing)
        if routing:
            for line in routing.workcenter_lines:
                if line.limited_production_capacity:
                    capacity_min = (
                        line.workcenter_id.capacity_per_cycle_min or
                        sys.float_info.min)
                    if capacity_min and qty < capacity_min:
                        qty = capacity_min
        return qty
