# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class QcTest(models.Model):
    _inherit = 'qc.test'

    automatic_claims = fields.Boolean('Automatic Claims', default=False)
