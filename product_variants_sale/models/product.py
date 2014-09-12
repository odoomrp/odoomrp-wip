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

    no_variants = fields.Boolean(string='Variants on sale',
                                 help='Create product variants when a sale'
                                 ' order is confirmed.')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    no_variants = fields.Boolean(string='Variants on sale',
                                 help='Create product variants when a sale'
                                 ' order is confirmed.')

    @api.multi
    def write(self, values):
        if not values.get('no_variants'):
            self.create_variant_ids(self.env.cr, self.env.uid, self.env.ids,
                                    context=self.env.context)
        return super(ProductTemplate, self).write(values)

    def create_variant_ids(self, cr, uid, ids, context=None):
        for tmpl in self.browse(cr, uid, ids, context=context):
            if tmpl.no_variants or tmpl.categ_id.no_variants:
                return True
            else:
                return super(ProductTemplate, self).create_variant_ids(
                    cr, uid, ids, context=context)
