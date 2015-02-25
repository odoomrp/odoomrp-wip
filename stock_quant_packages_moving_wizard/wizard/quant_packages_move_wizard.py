# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuantPackageMove(models.TransientModel):
    _name = 'stock.quant.package.move'

    pack_move_items = fields.One2many(
        comodel_name='stock.quant.package.move_items', inverse_name='move_id',
        string='Packs')

    def default_get(self, cr, uid, fields, context=None):
        res = super(StockQuantPackageMove, self).default_get(
            cr, uid, fields, context=context)
        packages_ids = context.get('active_ids', [])
        if not packages_ids:
            return res
        packages_obj = self.pool['stock.quant.package']
        packages = packages_obj.browse(cr, uid, packages_ids, context=context)
        items = []
        for package in packages:
            if not package.parent_id and package.location_id:
                item = {
                    'package': package.id,
                    'source_loc': package.location_id.id,
                }
                items.append(item)
        res.update(pack_move_items=items)
        return res

    @api.one
    def do_detailed_transfer(self):
        for item in self.pack_move_items:
            if item.dest_loc is not item.source_loc:
                for quant in item.package.quant_ids:
                    quant.move_to(item.dest_loc)
                for package in item.package.children_ids:
                    for quant in package.quant_ids:
                        quant.move_to(item.dest_loc)
        return True


class StockQuantPackageMoveItems(models.TransientModel):
    _name = 'stock.quant.package.move_items'
    _description = 'Picking wizard items'

    move_id = fields.Many2one(
        comodel_name='stock.quant.package.move', string='Package move')
    package = fields.Many2one(
        comodel_name='stock.quant.package', string='Quant package',
        domain=[('parent_id', '=', False), ('location_id', '!=', False)])
    source_loc = fields.Many2one(
        comodel_name='stock.location', string='Source Location', required=True)
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)

    @api.one
    @api.onchange('package')
    def onchange_quant(self):
        self.source_loc = self.package.location_id
