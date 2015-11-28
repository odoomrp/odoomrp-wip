# -*- coding: utf-8 -*-
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

    main_project_id = fields.Many2one('project.project',
                                      string="Main Project")

    @api.multi
    def set_main_project(self):
        procurement_obj = self.env['procurement.order']
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        for record in self:
            if mto_record in record.product_id.route_ids:
                if record.main_project_id:
                    main_project = record.main_project_id.id
                    if record.production_id:
                        record.production_id.project_id = main_project
                        for move in record.production_id.move_lines:
                            if mto_record in move.product_id.route_ids:
                                move.main_project_id = main_project
                                procurements = procurement_obj.search(
                                    [('move_dest_id', '=', move.id)])
                                procurements.write({'main_project_id':
                                                    main_project})
                                procurements.refresh()
                                procurements.set_main_project()
                    if record.move_ids:
                        for move in record.move_ids:
                            if mto_record in move.product_id.route_ids:
                                move.main_project_id = main_project
                                procurements = procurement_obj.search(
                                    [('move_dest_id', '=', move.id)])
                                procurements.write({'main_project_id':
                                                    main_project})
                                procurements.refresh()
                                procurements.set_main_project()
        return True

    @api.multi
    def run(self, autocommit=False):
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        for record in self:
            if mto_record not in record.product_id.route_ids:
                continue
            if record.move_dest_id:
                record.main_project_id = record.move_dest_id.main_project_id.id
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        self.set_main_project()
        return res
