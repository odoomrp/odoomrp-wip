# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    group_mrp_repair_cost_check = fields.Boolean(
        string='Mrp Repair Load Cost Visible',
        implied_group='mrp_repair_analytic.group_mrp_repair_cost_check')
