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

from openerp import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    parent_inherited = fields.Boolean('Inherits from parent')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_attributes_inherit_dict(self, product_attribute_list):
        product_attributes = self._get_product_attributes_dict()
        for attr in product_attributes:
            if self.env['product.attribute'].browse(
                    attr['attribute']).parent_inherited:
                for attr_line in product_attribute_list:
                    if attr_line.attribute.id == attr['attribute']:
                        attr.update({'value': attr_line.value.id})
        return product_attributes
