# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockHistory(models.Model):

    _inherit = 'stock.history'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(StockHistory, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        if ('manual_value' in fields) and ('real_value' in fields):
            group_lines = {}
            for line in res:
                domain = line.get('__domain', domain)
                group_lines.setdefault(
                    str(domain), self.search(domain))
            for line in res:
                manual_value = 0.0
                real_value = 0.0
                lines = group_lines.get(str(line.get('__domain', domain)))
                for pre_line in lines:
                    manual_value += (pre_line.product_id.manual_standard_cost *
                                     pre_line.quantity)
                    real_value += (pre_line.price_unit_on_quant *
                                   pre_line.quantity)
                line['real_value'] = real_value
                line['manual_value'] = manual_value
        return res

    @api.multi
    @api.depends("product_id", "product_id.manual_standard_cost", "quantity")
    def _compute_manual_value(self):
        for record in self:
            record.manual_value = (record.product_id.manual_standard_cost *
                                   record.quantity)

    @api.multi
    @api.depends('price_unit_on_quant', 'quantity')
    def _compute_real_value(self):
        for record in self:
            record.real_value = record.price_unit_on_quant * record.quantity

    manual_value = fields.Float(
        string="Manual Value", compute="_compute_manual_value")
    real_value = fields.Float(
        string="Real Value", compute="_compute_real_value")
