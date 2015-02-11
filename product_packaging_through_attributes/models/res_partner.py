# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    multiple_of_sec_pack = fields.Selection(
        selection=[('not', 'Not mandatory'), ('half', 'Half'),
                   ('full', 'Full')],
        string='Multiple of Secondary Packaging', default='not')
    partner_product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')
