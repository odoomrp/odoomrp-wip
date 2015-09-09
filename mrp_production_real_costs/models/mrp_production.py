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

from openerp import models, fields, api


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def calc_mrp_real_cost(self):
        self.ensure_one()
        return sum([-line.amount for line in
                    self.analytic_line_ids.filtered(lambda l: l.amount < 0)])

    @api.one
    @api.depends('analytic_line_ids', 'analytic_line_ids.amount',
                 'product_qty')
    def get_real_cost(self):
        self.real_cost = self.calc_mrp_real_cost()
        self.unit_real_cost = self.real_cost / self.product_qty

    @api.one
    @api.depends('avg_cost', 'real_cost')
    def get_percentage_difference(self):
        self.percentage_difference = 0
        if self.avg_cost and self.real_cost:
            self.percentage_difference = (self.real_cost * 100 / self.avg_cost)

    real_cost = fields.Float(
        "Total Real Cost", compute="get_real_cost", store=True)
    unit_real_cost = fields.Float(
        "Unit Real Cost", compute="get_real_cost", store=True)
    percentage_difference = fields.Float(
        "% difference", compute="get_percentage_difference", store=True)

    @api.multi
    def action_production_end(self):
        res = super(MrpProduction, self).action_production_end()
        for record in self:
            mrp_cost = record.calc_mrp_real_cost()
            done_lines = record.move_created_ids2.filtered(lambda l:
                                                           l.state == 'done')
            done_lines.create_produce_cost_line(mrp_cost)
            record.real_cost = mrp_cost
            done_lines.product_price_update_production_done()
        return res
