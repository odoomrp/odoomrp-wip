# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockQuantPackageMove(models.TransientModel):
    _name = 'stock.quant.package.move'

    pack_move_items = fields.One2many(
        comodel_name='stock.quant.package.move_items', inverse_name='move_id',
        string='Packs')

    @api.model
    def default_get(self, fields_list):
        res = super(StockQuantPackageMove, self).default_get(fields_list)
        packages_ids = self.env.context.get('active_ids', [])
        if not packages_ids:
            return res
        packages_obj = self.env['stock.quant.package']
        packages = packages_obj.browse(packages_ids)
        items = []
        for package in packages:
            if not package.parent_id and package.location_id:
                items.append({
                    'package': package.id,
                    # source_loc is needed even if it's a related field...
                    'source_loc': package.location_id.id,
                    })
        res.update(pack_move_items=items)
        return res

    @api.multi
    def do_detailed_transfer(self):
        self.ensure_one()
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
        required=True,
        domain=[('parent_id', '=', False), ('location_id', '!=', False)])
    source_loc = fields.Many2one(
        string='Current Location', related='package.location_id',
        readonly=True)
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)
