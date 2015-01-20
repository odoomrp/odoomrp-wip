# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class QcTest(models.Model):
    _inherit = 'qc.test'

    automatic_claims = fields.Boolean(
        'Automatic Claims', default=False,
        help="If you want to create one claim when the quality test status is"
             " 'Quality failed'.")
    automatic_claims_by_line = fields.Boolean(
        'Automatic Claims by line', default=False,
        help="If you want to create one claim per quality test line, when the"
             " quality test line status is 'No ok'.")
