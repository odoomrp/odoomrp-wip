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

from openerp import models, fields


class Task(models.Model):
    _inherit = "project.task"

    mrp_production_id = fields.Many2one('mrp.production',
                                        string='Manufacturing Order')
    mrp_sch_products = fields.One2many(
        "mrp.production.product.line", 'task_id',
        related='mrp_production_id.product_lines', store=False,
        string='Scheduled Products')
    wk_sch_products = fields.One2many(
        "mrp.production.product.line", 'task_id',
        related='wk_order.product_line', store=False,
        string='Scheduled Products')
    final_product = fields.Many2one('product.product',
                                    string='Product to Produce', store=False,
                                    related='mrp_production_id.product_id')
