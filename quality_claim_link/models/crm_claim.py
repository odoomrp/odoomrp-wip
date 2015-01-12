# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    inspection_id = fields.Many2one(
        comodel_name='qc.inspection', string='Inspection')
