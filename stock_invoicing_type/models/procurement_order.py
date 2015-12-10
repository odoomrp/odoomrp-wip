# -*- coding: utf-8 -*-
# (c) 2014-2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def run(self, autocommit=False):
        sale_obj = self.env['sale.order']
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        for stock_move in self.mapped('move_ids').filtered(
                lambda m: m.picking_id and not m.picking_id.invoice_type_id):
            orders = sale_obj.search([('procurement_group_id', '=',
                                       stock_move.group_id.id)])
            if orders:
                invoice_type = orders[0].invoice_type_id.id
                picking = stock_move.picking_id
                picking.invoice_type_id = invoice_type
        return res
