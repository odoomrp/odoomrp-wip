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


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    general_project_id = fields.Many2one('project.project',
                                         string="General Project")

    @api.multi
    def set_general_project(self):
        procurement_obj = self.env['procurement.order']
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        for record in self:
            if mto_record in record.product_id.route_ids:
                if record.general_project_id:
                    general_project = record.general_project_id.id
                    if record.production_id:
                        production = record.production_id
                        production.project_id = general_project
                        moves = production.move_lines
                        for move in moves:
                            if mto_record in move.product_id.route_ids:
                                move.general_project_id = general_project
                                procurements = procurement_obj.search(
                                    [('move_dest_id', '=', move.id)])
                                procurements.write({'general_project_id':
                                                    general_project})
                                procurements.refresh()
                                procurements.set_general_project()
                    if record.purchase_id:
                        purchase = record.purchase_id
                        purchase.general_project_id = general_project
                    if record.move_ids:
                        for move in record.move_ids:
                            if mto_record in move.product_id.route_ids:
                                move.general_project_id = general_project
                                procurements = procurement_obj.search(
                                    [('move_dest_id', '=', move.id)])
                                procurements.write({'general_project_id':
                                                    general_project})
                                procurements.refresh()
                                procurements.set_general_project()
        return True

    @api.multi
    def run(self):
        for record in self:
            general_project = False
            if record.sale_line_id:
                sale_id = record.sale_line_id.order_id
                general_project = sale_id.general_project_id.id
            elif record.move_dest_id:
                general_project = record.move_dest_id.general_project_id.id
            if general_project:
                record.general_project_id = general_project
        res = super(ProcurementOrder, self).run()
        self.set_general_project()
        return res
