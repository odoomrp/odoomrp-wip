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

    def _custumer_sequence_wa(self, vals, si_type, si_sequence):
        if si_type == 'customer' and si_sequence < 100:
            si_sequence += 100
        vals['type'] = si_type
        vals['sequence'] = si_sequence
        return vals

    @api.multi
    def write(self, vals):
        si_type = vals.get('type', self.type)
        si_sequence = vals.get('sequence', self.sequence)
        vals = self._custumer_sequence_wa(vals, si_type, si_sequence)
        return super(ProductSupplierinfo, self).write(vals)

    @api.model
    def create(self, vals):
        si_type = vals.get('type', 'supplier')
        si_sequence = vals.get('sequence', 1)
        vals = self._custumer_sequence_wa(vals, si_type, si_sequence)
        return super(ProductSupplierinfo, self).create(vals)
