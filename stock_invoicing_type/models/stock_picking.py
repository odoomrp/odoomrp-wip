# -*- coding: utf-8 -*-
# (c) 2014-2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_type_id = fields.Many2one(
        states={'draft': [('readonly', False)]})

    @api.multi
    def onchange_partner_id(self, partner_id=None):
        res = {}
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            res = {'value':
                   {'invoice_type_id': partner.property_invoice_type.id}}
        return res

    @api.multi
    def action_invoice_create(
            self, journal_id, group=False, type='out_invoice'):
        sale_journal_type = self.env['sale_journal.invoice.type']
        grouped_type = sale_journal_type.search(
            [('invoicing_method', '=', 'grouped')])
        result = []
        group_lst = self.filtered(lambda p: p.invoice_type_id in grouped_type)
        result += super(StockPicking, group_lst).action_invoice_create(
            journal_id, group=True, type=type)
        nogroup_lst = self.filtered(
            lambda p: p.invoice_type_id not in grouped_type)
        result += super(StockPicking, nogroup_lst).action_invoice_create(
            journal_id, group=False, type=type)
        return result
