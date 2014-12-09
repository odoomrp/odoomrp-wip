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

from openerp import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    def create_mo_from_packaging_operation(self):
        super(MrpProduction, self).create_mo_from_packaging_operation()
        for pack in self.pack:
            if (pack.processed and pack.packing_production and
                    (pack.packing_production.product_id.track_all or
                     pack.packing_production.product_id.track_production)):
                for line in pack.packing_production.product_lines:
                    if line.product_id == self.product_id:
                        for move in self.move_created_ids2:
                            if move.product_id == line.product_id:
                                line.lot = move.restrict_lot_id
