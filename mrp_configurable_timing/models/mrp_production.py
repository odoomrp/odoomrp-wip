# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields
import openerp.addons.decimal_precision as dp
import math


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    total_hours = fields.Float(digits=dp.get_precision('MRP Timing'))

    def _get_workorder_in_product_lines(
            self, workcenter_lines, product_lines, properties=None):
        super(MrpProduction, self)._get_workorder_in_product_lines(
            workcenter_lines, product_lines, properties=properties)
        for workorder in workcenter_lines:
            wc = workorder.routing_wc_line
            cycle = wc.cycle_nbr and (self.product_qty / wc.cycle_nbr) or 0
            if self.company_id.complete_cycle:
                cycle = int(math.ceil(cycle))
            workorder.cycle = cycle
            workorder.hour = wc.hour_nbr * cycle


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    total_hours = fields.Float(digits=dp.get_precision('MRP Timing'))
    hour = fields.Float(digits=dp.get_precision('MRP Timing'))


class MrpWorkcenter(models.Model):

    _inherit = 'mrp.workcenter'

    time_cycle = fields.Float(digits=dp.get_precision('MRP Timing'))


class MrpOperationWorkcenter(models.Model):

    _inherit = 'mrp.operation.workcenter'

    time_cycle = fields.Float(digits=dp.get_precision('MRP Timing'))


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    hour = fields.Float(digits=dp.get_precision('MRP Timing'))


class MrpRoutingWorkcenter(models.Model):

    _inherit = 'mrp.routing.workcenter'

    hour_nbr = fields.Float(digits=dp.get_precision('MRP Timing'))
