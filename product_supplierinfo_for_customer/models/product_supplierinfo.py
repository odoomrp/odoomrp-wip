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

from openerp import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    type = fields.Selection([('customer', 'Customer'),
                             ('supplier', 'Supplier')], string='Type',
                            default='supplier')

    @api.multi
    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'supplier':
            return {'domain': {'name': [('supplier', '=', True)]}}
        elif self.type == 'customer':
            return {'domain': {'name': [('customer', '=', True)]}}
        return {'domain': {'name': []}}

    def _custumer_sequence_wa(self, vals):
        si_type = vals['type'] if 'type' in vals else self.type
        si_sequence = vals['sequence'] if 'sequence' in vals else self.sequence
        if si_type == 'customer' and si_sequence < 100:
            vals['sequence'] += 100
        return vals

    @api.multi
    def write(self, vals):
        vals = self._custumer_sequence_wa(vals)
        return super(ProductSupplierinfo, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self._custumer_sequence_wa(vals)
        return super(ProductSupplierinfo, self).create(vals)
