
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 29/09/2014
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
    def action_confirm(self):
        picking_id = super(MrpProduction, self).action_confirm()
        move_obj = self.env['stock.move']
        mpwl_obj = self.env['mrp.production.workcenter.line']
        move_lst = move_obj.search([('production_id', '=', self.id)])
        for move in move_lst:
            for subp_line in self.bom_id.sub_products:
                if subp_line.operation:
                    if move.product_id.id == subp_line.product_id.id:
                        wo_lst = mpwl_obj.search(
                            [('production_id', '=', self.id),
                             ('routing_wc_line', '=', subp_line.operation.id)])
                        if wo_lst:
                            move.work_order = wo_lst[0].id
        return picking_id
