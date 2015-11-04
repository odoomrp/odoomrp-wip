# -*- coding: utf-8 -*-
# (c) 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _sale_order_line_count(self):
        for partner in self:
            partner.lines_count = len(partner.order_lines)

    order_lines = fields.One2many('sale.order.line', 'order_partner_id',
                                  'Sale order lines')
    lines_count = fields.Integer('Sale order lines',
                                 compute='_sale_order_line_count')
