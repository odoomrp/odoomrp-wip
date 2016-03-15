# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('reserved_quant_ids', 'quant_ids')
    def _compute_selected_lots(self):
        for record in self:
            quants = record.mapped('reserved_quant_ids') +\
                record.mapped('quant_ids')
            record.selected_lots = ', '.join(
                quants.mapped('lot_id.name'))

    selected_lots = fields.Char(
        string='Reserved Lots', compute='_compute_selected_lots')
