# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, exceptions, models, _


class ProductProduct(models.Model):
    # Redefine again the inheritance due to
    # https://github.com/odoo/odoo/issues/9084. This won't be needed on v10
    _inherit = ['product.product', 'product.configurator']
    _name = "product.product"

    @api.constrains('product_tmpl_id', 'attribute_value_ids')
    def _check_configuration_validity(self):
        """Totally overwritten for allowing some optional attributes."""
        attribute_line_model = self.env['product.attribute.line']
        for product in self:
            errors = []
            attribute_lines = product.product_tmpl_id.attribute_line_ids
            for value in product.attribute_value_ids:
                line = attribute_line_model.search(
                    [('attribute_id', '=', value.attribute_id.id),
                     ('product_tmpl_id', '=', product.product_tmpl_id.id)])
                attribute_lines -= line
            for line in attribute_lines.filtered('required'):
                errors.append(line.attribute_id.name)
            if errors:
                raise exceptions.ValidationError(
                    _("You have to fill the following attributes:\n%s") %
                    "\n".join(errors))
