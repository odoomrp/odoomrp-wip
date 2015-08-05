# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _make_consume_line_from_data(self, production, product, uom_id, qty,
                                     uos_id, uos_qty):
        move_id = super(MrpProduction, self)._make_consume_line_from_data(
            production, product, uom_id, qty, uos_id, uos_qty)
        if 'work_order' in self.env.context:
            move_obj = self.env['stock.move']
            work_order = self.env.context.get('work_order')
            picking_type = work_order.routing_wc_line.picking_type_id
            if picking_type:
                vals = {
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': (
                        picking_type.default_location_dest_id.id)}
                move_obj.browse(move_id).write(vals)
        return move_id
