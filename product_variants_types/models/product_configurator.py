# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, exceptions, fields, models, _


class ProductConfiguratorAttribute(models.Model):
    _inherit = 'product.configurator.attribute'

    custom_value = fields.Float(string='Custom value')
    attr_type = fields.Selection(
        string='Type', related='attribute_id.attr_type', readonly=True)

    def _is_custom_value_in_range(self):
        if self.attr_type == 'range':
            return (self.value_id.min_range <= self.custom_value <=
                    self.value_id.max_range)
        return True

    @api.multi
    @api.constrains('custom_value', 'attr_type', 'value_id')
    def _check_value_in_range(self):
        for record in self:
            if not record._is_custom_value_in_range():
                raise exceptions.Warning(
                    _("Custom value for attribute '%s' must be between %s and"
                      " %s.")
                    % (record.attribute_id.name, record.value_id.min_range,
                       record.value_id.max_range))

    @api.multi
    @api.onchange('custom_value', 'value_id')
    def _onchange_custom_value(self):
        self._check_value_in_range()

    @api.onchange('attribute_id', 'value_id')
    def onchange_attribute_id_product_variants_types(self):
        # HACK: This is needed because ORM is not updating the related field
        # when populating the one2many attribute list
        self.attr_type = self.attribute_id.attr_type
