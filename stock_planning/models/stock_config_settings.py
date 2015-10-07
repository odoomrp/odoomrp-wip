# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    group_cost_in_stock_planning = fields.Boolean(
        string='Show costs in stock planning',
        implied_group='stock_planning.group_stock_planning_show_costs')
