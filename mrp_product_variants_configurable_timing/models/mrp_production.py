# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models
import math


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

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
