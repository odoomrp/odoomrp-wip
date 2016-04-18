# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, exceptions, models, _


class ProductConfigurator(models.AbstractModel):
    _inherit = 'product.configurator'

    @api.model
    def check_configuration_validity(self, vals):
        # We override this for checking only required attributes
        attribute_line_model = self.env['product.attribute.line']
        errors = []
        for line_vals in vals.get('product_attribute_ids', []):
            line_vals = line_vals[2]
            if not line_vals.get('value_id'):
                line = attribute_line_model.search(
                    [('attribute_id', '=', line_vals['attribute_id']),
                     ('product_tmpl_id', '=', line_vals['product_tmpl_id'])])
                if line.required:
                    errors.append(line.attribute_id.name)
        if errors:
            raise exceptions.ValidationError(
                _("You have to fill the following attributes:\n%s") %
                "\n".join(errors))
