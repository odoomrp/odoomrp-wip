# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    no_create_variants = fields.Boolean(string='No automatic variants',
                                        help='This check disables the'
                                        ' automatic creation of product'
                                        ' variants.')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    no_create_variants = fields.Selection([('yes', 'Yes'), ('no', 'No'),
                                           ('empty',
                                            'Take the category value')],
                                          string='No automatic variants',
                                          help="This selection disables the"
                                          " automatic creation of product"
                                          " variants. If 'yes' it will not"
                                          " create the variants, if 'no'"
                                          " variants will be automatically"
                                          " generated and if empty it will"
                                          " check in the category.",
                                          required=True)

    @api.multi
    def create_variant_ids(self):
        for tmpl in self:
            if ((tmpl.no_create_variants == 'empty' and
                    not tmpl.categ_id.no_create_variants) or
                    (tmpl.no_create_variants == 'no')):
                return super(ProductTemplate, self).create_variant_ids()
            else:
                return True
