# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_product_variant_extended_description = fields.Boolean(
        'Use extended description when having product attributes',
        implied_group='sale_product_variants.'
                      'group_product_variant_extended_description')
