# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockQuantsMassiveMoveWizard(models.TransientModel):
    _name = 'stock.quants.massive_move'
    _description = 'Massive quant move'

    unreserve = fields.Boolean(default=True, help="If this option is selected, the quants will be unreserved before being moved. It should be checked when the Origin and Destination Locations are in different warehouses.")
    line_ids = fields.One2many(
        comodel_name='stock.quants.massive_move_items', inverse_name='move_id',
        string='Quants')

    @api.one
    def do_transfer(self):
        quant_obj = self.env['stock.quant']
        for line in self.line_ids:
            quants = quant_obj.search([
                ('location_id', '=', line.source_loc.id),
            ])
            for q in quants:
                if self.unreserve:
                    if q.reservation_id:
                        q.reservation_id.do_unreserve()
                q.move_to(line.dest_loc)
        return True


class StockQuantsMassiveMoveItems(models.TransientModel):
    _name = 'stock.quants.massive_move_items'
    _description = 'Massive quant move line'

    move_id = fields.Many2one(
        comodel_name='stock.quants.massive_move', string='Wizard')
    source_loc = fields.Many2one(
        comodel_name='stock.location', string='Source Location', required=True)
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)
