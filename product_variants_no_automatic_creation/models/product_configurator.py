# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, fields, models, exceptions, _
from openerp.addons import decimal_precision as dp


class ProductConfigurator(models.AbstractModel):
    _name = 'product.configurator'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        auto_join=True)
    product_attribute_ids = fields.One2many(
        comodel_name='product.configurator.attribute',
        domain=lambda self: [("owner_model", "=", self._name)],
        inverse_name='owner_id', string='Product attributes', copy=True)
    price_extra = fields.Float(
        compute='_compute_price_extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with the currently "
             "selected attributes values on sale price. eg. 200 price extra, "
             "1000 + 200 = 1200.")
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product")
    name = fields.Char()

    @api.multi
    @api.depends('product_attribute_ids', 'product_attribute_ids.value_id')
    def _compute_price_extra(self):
        for record in self:
            record.price_extra = sum(
                record.mapped('product_attribute_ids.price_extra'))

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        # First, empty current list
        self.product_attribute_ids = [
            (2, x.id) for x in self.product_attribute_ids]
        if not self.product_tmpl_id.attribute_line_ids:
            self.product_id = self.product_tmpl_id.product_variant_ids
        else:
            if not self.env.context.get('not_reset_product'):
                self.product_id = False
            attribute_list = []
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                attribute_list.append({
                    'attribute_id': attribute_line.attribute_id.id,
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'owner_model': self._name,
                    'owner_id': self.id,
                })
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
        # Needed because the compute method is not triggered
        self.product_attribute_ids._compute_possible_value_ids()
        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}

    @api.multi
    @api.onchange('product_attribute_ids')
    def onchange_product_attribute_ids(self):
        product_obj = self.env['product.product']
        domain, cont = product_obj._build_attributes_domain(
            self.product_tmpl_id, self.product_attribute_ids)
        self.product_id = False
        if cont:
            products = product_obj.search(domain)
            # Filter the product with the exact number of attributes values
            for product in products:
                if len(product.attribute_value_ids) == cont:
                    self.product_id = product.id
                    break
        if not self.product_id:
            self.name = self._get_product_description(
                self.product_tmpl_id, False,
                self.product_attribute_ids.mapped('value_id'))
        return {'domain': {'product_id': domain}}

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id_product_configurator(self):
        # First, empty current list
        self.product_attribute_ids = [
            (2, x.id) for x in self.product_attribute_ids]
        if self.product_id:
            attribute_list = (
                self.product_id._get_product_attributes_values_dict())
            for val in attribute_list:
                val['product_tmpl_id'] = self.product_id.product_tmpl_id
                val['owner_model'] = self._name
                val['owner_id'] = self.id
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
            self.name = self._get_product_description(
                self.product_id.product_tmpl_id, self.product_id,
                self.product_id.attribute_value_ids)

    @api.multi
    def onchange_product_id_product_configurator_old_api(self, product_id):
        """Method to be called in case inherited model use old API on_change.
        The returned result has to be merged with current 'value' key in the
        regular on_change method, not with the complete dictionary.

        :param product_id: ID of the changed product.
        :return: Dictionary with the changed values.
        """
        res = {}
        if product_id:
            product = self.env['product.product'].browse(product_id)
            attr_values_dict = product._get_product_attributes_values_dict()
            for val in attr_values_dict:
                val['product_tmpl_id'] = product.product_tmpl_id.id
                val['owner_model'] = self._name
                val['owner_id'] = self.id
            attr_values = [(0, 0, values) for values in attr_values_dict]
            res['product_attribute_ids'] = attr_values
            res['name'] = self._get_product_description(
                product.product_tmpl_id, product,
                product.attribute_value_ids)
        return res

    @api.model
    def _order_attributes(self, template, product_attribute_values):
        res = template._get_product_attributes_dict()
        res2 = []
        for val in res:
            value = product_attribute_values.filtered(
                lambda x: x.attribute_id.id == val['attribute_id'])
            if value:
                val['value_id'] = value
                res2.append(val)
        return res2

    @api.model
    def _get_product_description(self, template, product, product_attributes):
        name = product and product.name or template.name
        extended = self.user_has_groups(
            'product_variants_no_automatic_creation.'
            'group_product_variant_extended_description')
        if not product_attributes and product:
            product_attributes = product.attribute_value_ids
        values = self._order_attributes(template, product_attributes)
        if extended:
            description = "\n".join(
                "%s: %s" %
                (x['value_id'].attribute_id.name, x['value_id'].name)
                for x in values)
        else:
            description = ", ".join([x['value_id'].name for x in values])
        if not description:
            return name
        return ("%s\n%s" if extended else "%s (%s)") % (name, description)

    @api.multi
    def unlink(self):
        """Mimic `ondelete="cascade"`."""
        attributes = self.mapped("product_attribute_ids")
        result = super(ProductConfigurator, self).unlink()
        if result:
            attributes.unlink()
        return result

    @api.model
    def check_configuration_validity(self, vals):
        """This method checks that the current selection values are correct
        according rules. As default, the validity means that all the attributes
        values are set. This can be overridden to set another rules.

        :param vals: Dictionary of values that creates the record
        :type vals: dict
        :raises: exceptions.ValidationError: If the check is not valid.
        """
        if any(not x[2].get('value_id') for
               x in vals.get('product_attribute_ids', [])):
            raise exceptions.ValidationError(
                _("You have to fill all the attributes values."))


class ProductConfiguratorAttribute(models.Model):
    _name = 'product.configurator.attribute'

    owner_id = fields.Integer(string="Owner", required=True)
    owner_model = fields.Char(required=True)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        required=True)
    attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Attribute', readonly=True)
    value_id = fields.Many2one(
        comodel_name='product.attribute.value',
        domain="[('attribute_id', '=', attribute_id), "
               " ('id', 'in', possible_value_ids[0][2])]",
        string='Value')
    possible_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_compute_possible_value_ids')
    price_extra = fields.Float(
        compute='_compute_price_extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with this attribute "
             "value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")

    @api.multi
    @api.depends('attribute_id')
    def _compute_possible_value_ids(self):
        for record in self:
            # This should be unique due to the new constrain added
            attribute = record.product_tmpl_id.attribute_line_ids.filtered(
                lambda x: x.attribute_id == record.attribute_id)
            record.possible_value_ids = attribute.value_ids.sorted()

    @api.multi
    @api.depends('value_id')
    def _compute_price_extra(self):
        for record in self:
            record.price_extra = sum(
                record.value_id.price_ids.filtered(
                    lambda x: (
                        x.product_tmpl_id == record.product_tmpl_id)
                ).mapped('price_extra'))
