# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    plan = fields.Many2one('procurement.plan', string='Plan')
