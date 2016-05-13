# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, api, models


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    @api.multi
    @api.depends("product_id", "product_id.manual_standard_cost", "qty")
    def _compute_manual_value(self):
        for record in self:
            record.manual_value = (record.product_id.manual_standard_cost *
                                   record.qty)

    @api.multi
    @api.depends('cost', 'qty')
    def _compute_real_value(self):
        for record in self:
            record.real_value = record.cost * record.qty

    manual_value = fields.Float(
        string="Manual Value", store=True, compute="_compute_manual_value")
    real_value = fields.Float(
        string="Real Value", store=True, compute="_compute_real_value")
