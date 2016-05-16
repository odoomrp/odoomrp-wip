# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    parent_inherited = fields.Boolean(string='Inherits from parent')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_attribute_ids_inherit_dict(self, product_attribute_list):
        product_attribute_ids = self._get_product_attributes_dict()
        for attr in product_attribute_ids:
            if self.env['product.attribute'].browse(
                    attr['attribute_id']).parent_inherited:
                for attr_line in product_attribute_list:
                    if attr_line.attribute_id.id == attr['attribute_id']:
                        attr.update({'value_id': attr_line.value_id.id})
        return product_attribute_ids
