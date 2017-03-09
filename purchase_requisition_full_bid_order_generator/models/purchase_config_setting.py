# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api, fields


class purchase_config_settings(models.Model):
    _inherit = 'purchase.config.settings'

    rfq_to_suppliers = fields.Selection([('a', 'Create RFQ to only suppliers, with all the products'),
                                         ('s', 'Create RFQ to all the suppliers with available products')],
                                        string='RFQ from Bids')

    @api.multi
    def get_default_rfq_to_suppliers(self):
        return {'rfq_to_suppliers': self.env.user.company_id.rfq_to_suppliers}

    @api.one
    def set_default_rfq_to_suppliers(self):
        self.env.user.company_id.write({'rfq_to_suppliers': self.rfq_to_suppliers})
        return True
