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
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_mo(self):
        production_obj = self.env['mrp.production']
        result = super(ProcurementOrder, self).make_mo()
        procurement = self.browse(result.keys()[0])
        production = production_obj.browse(result.values()[0])
        if procurement.plan:
            production.write({'plan': procurement.plan.id})
        return result

    @api.multi
    def set_main_plan(self):
        procurement_obj = self.env['procurement.order']
        for record in self:
            if record.production_id:
                production = record.production_id
                if production.plan:
                    moves = production.move_lines
                    for move in moves:
                        procurements = procurement_obj.search(
                            [('move_dest_id', '=', move.id)])
                        procurements.write({'plan': production.plan.id})
                        procurements.refresh()
                        procurements.set_main_plan()
                    if record.move_ids:
                        for move in record.move_ids:
                            procurements = procurement_obj.search(
                                [('move_dest_id', '=', move.id)])
                            procurements.write({'plan': production.plan.id})
                            procurements.refresh()
                            procurements.set_main_plan()
        return True

    @api.multi
    def run(self, autocommit=False):
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        self.set_main_plan()
        return res


class ProcurementPlan(models.Model):
    _inherit = 'procurement.plan'

    production_ids = fields.One2many(
        'mrp.production', 'plan', string='Productions', readonly=True)
