
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class WizProductionProductLine(models.TransientModel):
    _inherit = 'wiz.production.product.line'

    lot = fields.Many2one('stock.production.lot', 'Reserved Lot')

    def _prepare_product_addition(self, product, product_qty, production):
        addition_vals = super(
            WizProductionProductLine, self)._prepare_product_addition(
            product, product_qty, production)
        if self.lot:
            addition_vals['lot'] = self.lot.id
        return addition_vals

    @api.multi
    def add_product(self):
        production_obj = self.env['mrp.production']
        if self.lot:
            available = production_obj._check_lot_quantity(
                self.lot.id, self.production_id.location_src_id.id,
                self.product_qty)
            if not available:
                raise exceptions.Warning(
                    _('No Lot Available'), _('There is no lot %s available for'
                                             ' product') % (self.lot.name))
        res = super(WizProductionProductLine, self).add_product()
        return res
