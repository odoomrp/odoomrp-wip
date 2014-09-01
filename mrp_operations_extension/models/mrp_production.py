
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 28/08/2014
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

    @api.model
    def _make_consume_line_from_data(self, production, product, uom_id,
                                     qty, uos_id, uos_qty):
        res = super(MrpProduction, self)._make_consume_line_from_data(
            production, product, uom_id, qty, uos_id, uos_qty)
        mppl_lines = production.product_lines
        st_move = self.env['stock.move'].browse(res)
        for line in mppl_lines:
            if st_move.product_id.id == line.product_id.id:
                st_move.operation = line.operation.id
        return res


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    operation = fields.Many2one('mrp.routing.workcenter', 'Operation')
