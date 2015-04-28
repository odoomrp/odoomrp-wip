# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manual_production_lot = fields.Char(string='Manual Production Lot')
    concatenate_lots_components = fields.Boolean(
        string='Concatenate Lots Components')

    @api.model
    def action_produce(
            self, production_id, production_qty, production_mode, wiz=False):
        lot_obj = self.env['stock.production.lot']
        if production_mode == 'consume_produce' and wiz:
            production = self.browse(production_id)
            if (production.product_id.track_all or
                production.product_id.track_production or
                    production.product_id.track_incoming):
                lot_id = False
                for line in production.move_created_ids2:
                    if (line.product_id.id == production.product_id.id and
                            line.restrict_lot_id):
                        lot_id = line.restric_lot_id.id
                        break
                if not lot_id:
                    code = production.manual_production_lot or ''
                    if production.concatenate_lots_components:
                        lot_ids = set()
                        for line in wiz.consume_lines:
                            if line.lot_id:
                                lot_ids.add(line.lot_id)
                        for line in production.move_lines2:
                            if line.restrict_lot_id:
                                lot_ids.add(line.restrict_lot_id)
                        for lot in lot_ids:
                            code += '-%s' % lot.name
                    vals = {'name': code,
                            'product_id': production.product_id.id}
                    new_lot = lot_obj.create(vals)
                vals = {'lot_id': new_lot.id}
                wiz.write(vals)
        return super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz=wiz)
