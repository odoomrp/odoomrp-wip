# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    no_create_variants = fields.Boolean(
        string="Don't create variants automatically",
        help='This check disables the automatic creation of product variants '
             'for all the products of this category.',
        default=True)

    @api.multi
    @api.onchange('no_create_variants')
    def onchange_no_create_variants(self):
        self.ensure_one()
        if not self._origin:
            return {}
        return {'warning': {'title': _('Change warning!'),
                            'message': _('Changing this parameter may cause'
                                         ' automatic variants creation')}}

    @api.multi
    def write(self, values):
        res = super(ProductCategory, self).write(values)
        if ('no_create_variants' in values and
                not values.get('no_create_variants')):
            self.env['product.template'].search(
                [('categ_id', '=', self.id),
                 ('no_create_variants', '=', 'empty')]).create_variant_ids()
        return res
