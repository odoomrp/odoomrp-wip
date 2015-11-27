# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _make_production_consume_line(self, line):
        res = super(MrpProduction, self)._make_production_consume_line(line)
        if line.lot and res:
            st_move_obj = self.env['stock.move']
            move = st_move_obj.browse(res)
            move.restrict_lot_id = line.lot.id
        return res

    def _check_lot_quantity(self, lot_id, location_id, quantity):
        """ Returns if there is enough product quantity for a lot in a
        defined location.
        @param lot_id: Lot id to check
        @param location_id: Location id to check
        @param quantity: Quantity expected
        """
        aval_quant_lst = self.env['stock.quant'].search([
            ('lot_id', '=', lot_id),
            ('location_id', '=', location_id)
        ])
        if aval_quant_lst and sum(aval_quant_lst.mapped('qty')) >= quantity:
            return True
        return False


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    lot = fields.Many2one('stock.production.lot', 'Reserved Lot')
