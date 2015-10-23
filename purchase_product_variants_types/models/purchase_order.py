# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PurchaseOrderLineAttribute(models.Model):
    _inherit = 'purchase.order.line.attribute'

    custom_value = fields.Float(string='Custom value')
    attr_type = fields.Selection(
        string='Type', store=False, related='attribute.attr_type')

    def _is_custom_value_in_range(self):
        if self.attr_type == 'range':
            return (self.value.min_range <= self.custom_value <=
                    self.value.max_range)
        return True

    @api.one
    @api.constrains('custom_value', 'attr_type', 'value')
    def _custom_value_in_range(self):
        if not self._is_custom_value_in_range():
            raise UserError(
                _("Custom value for attribute '%s' must be between %s and"
                  " %s.")
                % (self.attribute.name, self.value.min_range,
                   self.value.max_range))

    @api.one
    @api.onchange('custom_value', 'value')
    def _onchange_custom_value(self):
        self._custom_value_in_range()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.one
    def _check_line_confirmability(self):
        for line in self.product_attributes:
            if line.value:
                continue
            attribute_line = self.product_template.attribute_line_ids.filtered(
                lambda x: x.attribute_id == line.attribute)
            if attribute_line.required:
                raise UserError(
                    _("You cannot confirm before configuring all values "
                      "of required attributes. Product: %s Attribute: %s.") %
                    (self.product_template.name, attribute_line.display_name))
