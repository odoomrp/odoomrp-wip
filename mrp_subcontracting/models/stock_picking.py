# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_production = fields.Many2one('mrp.production', 'MPR Production')
