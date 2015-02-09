# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    multiple_of_pallet = fields.Selection(
        selection=[('not', 'Not mandatory'), ('half', 'Half pallet'),
                   ('full', 'Full pallet')],
        string='Multiple of pallet', default='not')
    partner_product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit',
        domain="[('type','=','pallet')]")
