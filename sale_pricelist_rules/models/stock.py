# -*- coding: utf-8 -*-
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(
            move, partner, inv_type)
        if inv_type in ('out_invoice', 'out_refund'):
            if move.procurement_id and move.procurement_id.sale_line_id:
                res.update({
                    "discount2": move.procurement_id.sale_line_id.discount2,
                    "discount3": move.procurement_id.sale_line_id.discount3
                })
        return res
