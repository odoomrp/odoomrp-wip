# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpTrackLot(models.Model):
    _inherit = "mrp.track.lot"

    workcenter_line = fields.Many2one(
        'mrp.production.workcenter.line', 'Work Order')
