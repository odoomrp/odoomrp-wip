# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuantsMoveWizard(models.TransientModel):
    _name = 'stock.quants.move'

    pack_move_items = fields.One2many(
        comodel_name='stock.quants.move_items', inverse_name='move_id',
        string='Quants')
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)

    def default_get(self, cr, uid, fields, context=None):
        res = super(StockQuantsMoveWizard, self).default_get(
            cr, uid, fields, context=context)
        quants_ids = context.get('active_ids', [])
        if not quants_ids:
            return res
        quant_obj = self.pool['stock.quant']
        quants = quant_obj.browse(cr, uid, quants_ids, context=context)
        items = []
        for quant in quants:
            if not quant.package_id:
                item = {
                    'quant': quant.id,
                    'source_loc': quant.location_id.id,
                }
                items.append(item)
        res.update(pack_move_items=items)
        return res

    @api.one
    def do_transfer(self):
        for item in self.pack_move_items:
            item.quant.move_to(self.dest_loc)
        return True


class StockQuantsMoveItems(models.TransientModel):
    _name = 'stock.quants.move_items'
    _description = 'Picking wizard items'

    move_id = fields.Many2one(
        comodel_name='stock.quants.move', string='Quant move')
    quant = fields.Many2one(
        comodel_name='stock.quant', string='Quant',
        domain=[('package_id', '=', False)])
    source_loc = fields.Many2one(
        comodel_name='stock.location', string='Source Location', required=True)

    @api.one
    @api.onchange('quant')
    def onchange_quant(self):
        self.source_loc = self.quant.location_id
