# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_attributes_dict(self):
        product_attributes = super(ProductTemplate,
                                   self)._get_product_attributes_dict()
        for attribute in product_attributes:
            line = self.env['product.attribute.line'].search(
                [('attribute_id', '=', attribute['attribute']),
                 ('product_tmpl_id', '=', self.id)])
            attribute.update(
                {'value': line and line[0].default.id})
        return product_attributes
