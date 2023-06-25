# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api, fields


class res_company(models.Model):
    _inherit = 'res.company'

    rfq_to_suppliers = fields.Selection([('a', 'To All Products'), ('s', 'To All Suppliers')], default='a',
                                        required=True, string='RFQ from Bids')
