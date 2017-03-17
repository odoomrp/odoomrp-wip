# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockQuantMove(models.TransientModel):
    _name = 'stock.quant.move'

    # TODO port v9: rename this field to remove 'pack_', which is confusing
    pack_move_items = fields.One2many(
        comodel_name='stock.quant.move_items', inverse_name='move_id',
        string='Packs')

    @api.model
    def default_get(self, fields_list):
        res = super(StockQuantMove, self).default_get(fields_list)
        quants_ids = self.env.context.get('active_ids', [])
        if not quants_ids:
            return res
        quant_obj = self.env['stock.quant']
        quants = quant_obj.browse(quants_ids)
        items = []
        for quant in quants:
            if not quant.package_id:
                items.append({
                    'quant': quant.id,
                    # source_loc is needed even if it's a related field...
                    'source_loc': quant.location_id.id,
                    })
        res.update(pack_move_items=items)
        return res

    @api.one
    def do_transfer(self):
        for item in self.pack_move_items:
            item.quant.move_to(item.dest_loc)
        return True


class StockQuantMoveItems(models.TransientModel):
    _name = 'stock.quant.move_items'
    _description = 'Picking wizard items'

    move_id = fields.Many2one(
        comodel_name='stock.quant.move', string='Quant move')
    quant = fields.Many2one(
        comodel_name='stock.quant', string='Quant', required=True,
        domain=[('package_id', '=', False)])
    source_loc = fields.Many2one(
        string='Current Location', related='quant.location_id', readonly=True)
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)
