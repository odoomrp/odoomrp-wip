# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, exceptions, fields, models, _


class ProductProduct(models.Model):
    _inherit = ['product.product', 'product.configurator']
    _name = "product.product"

    # This is needed as the AbstractModel removes the delegated related field
    name = fields.Char(related="product_tmpl_id.name")

    @api.multi
    def _get_product_attributes_values_dict(self):
        # Retrieve first the attributes from template to preserve order
        res = self.product_tmpl_id._get_product_attributes_dict()
        for val in res:
            value = self.attribute_value_ids.filtered(
                lambda x: x.attribute_id.id == val['attribute_id'])
            val['value_id'] = value.id
        return res

    @api.multi
    def _get_product_attributes_values_text(self):
        description = self.attribute_value_ids.mapped(
            lambda x: "%s: %s" % (x.attribute_id.name, x.name))
        return "%s\n%s" % (self.product_tmpl_id.name, "\n".join(description))

    @api.model
    def _build_attributes_domain(self, product_template, product_attributes):
        domain = []
        cont = 0
        if product_template:
            domain.append(('product_tmpl_id', '=', product_template.id))
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    value_id = attr_line.get('value_id')
                else:
                    value_id = attr_line.value_id.id
                if value_id:
                    domain.append(('attribute_value_ids', '=', value_id))
                    cont += 1
        return domain, cont

    @api.model
    def _product_find(self, product_template, product_attributes):
        if product_template:
            domain, cont = self._build_attributes_domain(
                product_template, product_attributes)
            products = self.search(domain)
            # Filter the product with the exact number of attributes values
            for product in products:
                if len(product.attribute_value_ids) == cont:
                    return product
        return False

    @api.constrains('product_tmpl_id', 'attribute_value_ids')
    def _check_duplicity(self):
        for product in self:
            domain = [('product_tmpl_id', '=', product.product_tmpl_id.id)]
            for value in product.attribute_value_ids:
                domain.append(('attribute_value_ids', '=', value.id))
            other_products = self.search(domain)
            # Filter the product with the exact number of attributes values
            cont = len(product.attribute_value_ids)
            for other_product in other_products:
                if (len(other_product.attribute_value_ids) == cont and
                        other_product != product):
                    raise exceptions.ValidationError(
                        _("There's another product with the same attributes."))

    @api.constrains('product_tmpl_id', 'attribute_value_ids')
    def _check_configuration_validity(self):
        """This method checks that the current selection values are correct
        according rules. As default, the validity means that all the attributes
        values are set. This can be overridden to set another rules.

        :raises: exceptions.ValidationError: If the check is not valid.
        """
        for product in self:
            if bool(product.product_tmpl_id.attribute_line_ids.mapped(
                    'attribute_id') -
                    product.attribute_line_ids.mapped('attribute_id')):
                raise exceptions.ValidationError(
                    _("You have to fill all the attributes values."))

    @api.model
    def create(self, vals):
        if (not vals.get('attribute_value_ids') and
                vals.get('product_attribute_ids')):
            vals['attribute_value_ids'] = (
                (4, x[2]['value_id'])
                for x in vals.pop('product_attribute_ids')
                if x[2].get('value_id'))
        obj = self.with_context(product_name=vals.get('name', ''))
        return super(ProductProduct, obj).create(vals)
