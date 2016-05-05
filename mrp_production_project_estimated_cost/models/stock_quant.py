# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models, api


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    @api.one
    @api.depends("product_id", "product_id.manual_standard_cost", "qty")
    def _compute_manual_value(self):
        for record in self:
            record.manual_value = (record.product_id.manual_standard_cost *
                                   record.qty)

    manual_value = fields.Float(
        string="Manual Value", store=True, compute="_compute_manual_value")
