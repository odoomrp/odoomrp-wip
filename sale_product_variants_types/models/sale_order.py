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

from openerp import models, fields, api, exceptions, _


class SaleOrderLineAttribute(models.Model):
    _inherit = 'sale.order.line.attribute'

    custom_value = fields.Float(string='Custom value')
    attr_type = fields.Selection(string='Type', store=False,
                                 related='attribute.attr_type')

    @api.one
    @api.constrains('custom_value')
    def _custom_value_in_range(self):
        if not (self.value.min_range <= self.custom_value and 
                self.value.max_range >= self.custom_value):
            raise exceptions.Warning(
                _("Custom value from attribute '%s' must be between %s and %s.")
                % (self.attribute.name, self.value.min_range,
                   self.value.max_range))
