# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'ref_customer': fields.char('Customer Reference', size=64,
                                    help='This is my customer reference for'
                                    ' the supplier'),
        'ref_supplier': fields.char('Supplier Reference', size=64,
                                    help='This is my supplier reference for'
                                    ' the customer'),
    }
