# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    picking_out = fields.Many2one('stock.picking', string='Picking Out',
                                  readonly=True)

    def _prepare_stock_picking(self, move):
        StockPickingType = self.env['stock.picking.type']
        outgoing_type = StockPickingType.search(
            [('code', '=', 'outgoing'),
             ('warehouse_id', '=', move.warehouse_id.id)])[:1]
        values = {'origin': move.origin,
                  'company_id': move.company_id.id,
                  'move_type': move.group_id.move_type or 'direct',
                  'partner_id': move.partner_id.id,
                  'picking_type_id': outgoing_type.id
                  }
        return values

    @api.multi
    def action_repair_done(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        res = super(MrpRepair, self).action_repair_done()
        StockLocation = self.pool.get("stock.location")
        StockPicking = self.env['stock.picking']
        if self.address_id and self.move_id:
            wh_id = StockLocation.get_warehouse(
                self.env.cr, self.env.uid, self.location_dest_id,
                self.env.context)
            if not self.move_id.warehouse_id:
                self.move_id.warehouse_id = wh_id
            values = self._prepare_stock_picking(self.move_id)
            pick = StockPicking.create(values)
            self.picking_out = pick
            self.move_id.write({'picking_type_id': pick.picking_type_id.id,
                                'picking_id': pick.id})
        return res
