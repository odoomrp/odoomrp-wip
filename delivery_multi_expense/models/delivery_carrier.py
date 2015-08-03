# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    transport = fields.Boolean(
        'Is transporter', default=True, help="Determines whether the carrier"
        " method")
