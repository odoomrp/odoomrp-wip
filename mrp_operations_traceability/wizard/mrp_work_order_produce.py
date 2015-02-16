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


class MrpWorkOrderProduce(models.TransientModel):
    _inherit = 'mrp.work.order.produce'

    @api.multi
    def do_produce(self):
        result = super(MrpWorkOrderProduce, self).do_produce()
        work_line = self.env['mrp.production.workcenter.line'].browse(
            self.env.context['active_id'])
        for data in self:
            if data.lot_id:
                for move in work_line.production_id.move_lines2:
                    if not move.prod_parent_lot:
                        move.prod_parent_lot = data.lot_id.id
                        self._create_track_lot_from_work_order(
                            move, data.lot_id, work_line)
        return result

    @api.multi
    def do_consume(self):
        result = super(MrpWorkOrderProduce, self).do_consume()
        work_line = self.env['mrp.production.workcenter.line'].browse(
            self.env.context['active_id'])
        for data in self:
            if data.lot_id:
                for move in work_line.production_id.move_lines2:
                    if not move.prod_parent_lot:
                        move.prod_parent_lot = data.lot_id.id
                        self._create_track_lot_from_work_order(
                            move, data.lot_id, work_line)
        return result

    @api.multi
    def do_consume_produce(self):
        result = super(MrpWorkOrderProduce, self).do_consume_produce()
        work_line = self.env['mrp.production.workcenter.line'].browse(
            self.env.context['active_id'])
        for data in self:
            if data.lot_id:
                for move in work_line.production_id.move_lines2:
                    if not move.prod_parent_lot:
                        move.prod_parent_lot = data.lot_id.id
                        self._create_track_lot_from_work_order(
                            move, data.lot_id, work_line)
        return result

    def _create_track_lot_from_work_order(self, move, lot, work_line):
        track_lot_obj = self.env['mrp.track.lot']
        track_lot_obj.create(
            {'component': move.product_id.id,
             'component_lot': move.restrict_lot_id.id,
             'product': work_line.production_id.product_id.id,
             'product_lot': lot.id,
             'production': work_line.production_id.id,
             'workcenter_line': work_line.id,
             'st_move': move.id})
