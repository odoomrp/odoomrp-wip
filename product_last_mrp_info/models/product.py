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


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.one
    @api.depends('last_mrp_id')
    def _get_mrp_last_cost(self):
        analytic_line_obj = self.env['account.analytic.line']
        last_mrp_cost = 0.0
        if self.last_mrp_id:
            analytic_lines = analytic_line_obj.search(
                [('mrp_production_id', '=', self.last_mrp_id.id)])
            if analytic_lines:
                last_mrp_cost = sum([-line.amount for line in analytic_lines])
        self.last_mrp_cost = last_mrp_cost

    last_mrp_id = fields.Many2one('mrp.production',
                                  string="Last Manufacturing Order")
    last_mrp_cost = fields.Float(string="Last manufacturing order cost",
                                 compute=_get_mrp_last_cost, store=True)
    last_mrp_date = fields.Datetime(string="Last manufacturing order date",
                                    related="last_mrp_id.date_finished")
