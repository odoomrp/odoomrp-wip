# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class AssignManualQuants(models.TransientModel):
    _inherit = 'assign.manual.quants'

    @api.model
    def default_get(self, var_fields):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        if (move.raw_material_production_id and
                move.raw_material_production_id.production and
                move.raw_material_production_id.production.move_created_ids2):
            parent = move.raw_material_production_id.production
            domain = ['|', ('location_id', '=', move.location_id.id),
                      ('location_id', 'in', move.location_id.child_ids.ids),
                      ('product_id', '=', move.product_id.id),
                      ('qty', '>', 0), ('reservation_id', '=', False)]
            for created_product in parent.move_created_ids2:
                if move.product_id == created_product.product_id:
                    domain += [('history_ids', 'in',
                                parent.move_created_ids2.ids)]
                    break
            available_quants_ids = self.env['stock.quant'].search(domain)
            available_quants = [{'quant': x.id,
                                 'lot_id': x.lot_id.id,
                                 'package_id': x.package_id.id,
                                 'location_id': x.location_id.id}
                                for x in available_quants_ids]
            available_quants.extend({
                'quant': x.id,
                'selected': True,
                'lot_id': x.lot_id.id,
                'location_id': x.location_id.id,
                'qty': x.qty} for x in move.reserved_quant_ids
            )
            return {'quants_lines': available_quants}
        else:
            return super(AssignManualQuants, self).default_get(var_fields)
