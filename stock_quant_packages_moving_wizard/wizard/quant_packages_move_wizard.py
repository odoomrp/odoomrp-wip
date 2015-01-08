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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields


class StockQuantPackageMove(models.TransientModel):
    _name = 'stock.quant.package.move'

    pack_move_items = fields.One2many(
        comodel_name='stock.quant.package.move_items', inverse_name='move_id',
        string='Packs')

    def default_get(self, cr, uid, fields, context=None):
        res = super(StockQuantPackageMove, self).default_get(
            cr, uid, fields, context=context)
        quants_ids = context.get('active_ids', [])
        if not quants_ids:
            return res
        quant_obj = self.pool['stock.quant']
        quants = quant_obj.browse(cr, uid, quants_ids, context=context)
        items = []
        for quant in quants:
            item = {
                'quant': quant.id,
                'source_pkg': quant.package_id.id,
                'source_loc': quant.location_id.id,
            }
            items.append(item)
        res.update(pack_move_items=items)
        return res


class StockQuantPackageMoveItems(models.TransientModel):
    _name = 'stock.quant.package.move_items'
    _description = 'Picking wizard items'

    move_id = fields.Many2one(
        comodel_name='stock.quant.package.move', string='Package move')
    quant = fields.Many2one(
        comodel_name='stock.quant', string='Quant')
    source_pkg = fields.Many2one(
        comodel_name='stock.quant.package', string='Source package',
        domain="['|', ('location_id', 'child_of', source_loc),"
        " ('location_id','=',False)]")
    source_loc = fields.Many2one(
        comodel_name='stock.location', string='Source Location', required=True)
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)
    dest_pkg = fields.Many2one(
        comodel_name='stock.quant.package', string='Destination package',
        domain="['|', ('location_id', 'child_of', dest_loc),"
        " ('location_id','=',False)]")
