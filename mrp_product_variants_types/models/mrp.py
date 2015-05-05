# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, exceptions, _


class SaleOrderLineAttribute(models.Model):
    _inherit = 'mrp.production.attribute'

    custom_value = fields.Float(string='Custom value')
    attr_type = fields.Selection(string='Type', store=False,
                                 related='attribute.attr_type')

    def _is_custom_value_in_range(self):
        if self.attr_type == 'range':
            if not (self.value.min_range <= self.custom_value and
                    self.value.max_range >= self.custom_value):
                return False
        return True

    @api.one
    @api.constrains('custom_value', 'attr_type', 'value')
    def _custom_value_in_range(self):
        if not self._is_custom_value_in_range():
            raise exceptions.Warning(
                _("Custom value for attribute '%s' must be between %s and"
                  " %s.")
                % (self.attribute.name, self.value.min_range,
                   self.value.max_range))

    @api.one
    @api.onchange('custom_value', 'value')
    def _onchange_custom_value(self):
        self._custom_value_in_range()
