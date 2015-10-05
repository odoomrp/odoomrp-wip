# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockReservation(models.Model):
    _inherit = 'stock.reservation'
    procurement_from_plan = fields.Many2one(
        'procurement.order', string='Procurement from plan')
