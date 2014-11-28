
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


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_lot_in_move_lines(self, product_lines, move_lines):
        for move_line in move_lines:
            for product_line in product_lines:
                if product_line.product_id.id == move_line.product_id.id:
                    move_line.restrict_lot_id = product_line.lot.id

    @api.multi
    def action_confirm(self):
        quant_obj = self.env['stock.quant']
        available = True
        for line in self.product_lines:
            if line.lot and available:
                aval_quant_lst = quant_obj.search(
                    [('lot_id', '=', line.lot.id),
                     ('location_id', '=', self.location_src_id.id)])
                if aval_quant_lst:
                    quantity = line.product_qty
                    available_qty = sum([x.qty for x in aval_quant_lst])
                    if quantity >= available_qty:
                        available = False
                        break
                else:
                    available = False
        if not available:
            raise exceptions.Warning(
                _('No Lot Available'), _('There is no product available for '
                                         'lot: %s') % line.lot.name)
        res = super(MrpProduction, self).action_confirm()
        self._get_lot_in_move_lines(self.product_lines, self.move_lines)
        return res


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    lot = fields.Many2one('stock.production.lot', 'Reserved Lot')
