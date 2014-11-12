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

from openerp import models, api


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def action_production_end(self):
        analytic_line_obj = self.env['account.analytic.line']
        result = super(MrpProduction, self).action_production_end()
        for record in self:
            product = record.product_id
            analytic_lines = analytic_line_obj.search(
                [('mrp_production_id', '=', record.id)])
            total_cost = 0.0
            if analytic_lines:
                total_cost = sum([-line.amount for line in analytic_lines])
            product.last_mrp_date = record.date_finished
            print total_cost
            product.last_mrp_cost = total_cost
        return result
