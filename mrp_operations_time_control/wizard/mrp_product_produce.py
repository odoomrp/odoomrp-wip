
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2013 AvanzOSC S.L. (Mikel Arregi) All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp import api, fields, models


class MrpWorkOrderProduce(models.TransientModel):
    
    _name = "mrp.work.order.produce"

    def _get_product_id(self):
        """ To obtain product id
        @return: id
        """
        prod=False
        if self.env.context.get("active_id"):
            work_line = self.env['mrp.production.workcenter.line'].browse(self.env.context.get("active_id"))
            prod = work_line.production_id
        return prod and prod.product_id or False

    def _get_track(self):
        prod = self._get_product_id()
        return prod and prod.track_production or False

    def do_produce(self, cr, uid, ids, context=None):
        work_line = self.pool['mrp.production.workcenter.line'].browse(cr, uid, context.get("active_id"), context=context)
        production_id = work_line.production_id.id
        assert production_id, "Production Id should be specified in context as a Active ID."
        data = self.browse(cr, uid, ids[0], context=context)
        self.pool['mrp.production'].action_produce(cr, uid, production_id,
                            False, data.mode, data, context=context)
        return {}

    product_id = fields.Many2one('product.product', string='Product', default=_get_product_id)
    #product_qty = fields.Float('Select Quantity', digits=(12,6), required=True, default=_get_product_qty)
    mode = fields.Selection([('consume', 'Consume Only')], string='Mode', required=True, readonly=True, default='consume')
    #lot_id = fields.Many2one('stock.production.lot', 'Lot')
    consume_lines = fields.One2many('mrp.product.produce.line', 'work_produce_id', string='Products Consumed')
    track_production = fields.Boolean('Track production', default=_get_track)

class mrp_product_produce_line(models.TransientModel):
    _inherit = "mrp.product.produce.line"
    
    work_produce_id = fields.Many2one('mrp.work.order.produce')
