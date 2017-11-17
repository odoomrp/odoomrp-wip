# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    group_mrp_repair_cost_check = fields.Boolean(
        string='Mrp Repair Load Cost Visible',
        implied_group='mrp_repair_analytic.group_mrp_repair_cost_check')
