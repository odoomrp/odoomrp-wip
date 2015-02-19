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


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(
            self, bom, product, factor, properties=None, level=0,
            routing_id=False, previous_products=None, master_bom=None,
            production=None):
        return self._bom_explode_variants(
            bom, product, factor, properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom, production=production)

    @api.model
    def _bom_explode_variants(
            self, bom, product, factor, properties=None, level=0,
            routing_id=False, previous_products=None, master_bom=None,
            production=None):
        routing_id = bom.routing_id.id or routing_id
        result, result2 = super(MrpBom, self)._bom_explode_variants(
            bom, product, factor, properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom, production=production)
        result2 = self._get_workorder_operations(
            result2, factor=factor, level=level, routing_id=routing_id)
        return result, result2
