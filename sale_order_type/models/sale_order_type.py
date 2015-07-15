# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class SaleOrderTypology(models.Model):

    _name = 'sale.order.type'
    _description = 'Type of sale order'

    refund_journal_id = fields.Many2one(
        'account.journal', string='Refund Billing Journal')
    description = fields.Text('Description')
    journal_id = fields.Many2one(
        'account.journal', string='Billing Journal')
    name = fields.Char(string='Name', required=True)
    sequence_id = fields.Many2one(
        'ir.sequence', string='Entry Sequence', copy=False)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=False)
    proof = fields.Boolean('Proof', copy=False)
