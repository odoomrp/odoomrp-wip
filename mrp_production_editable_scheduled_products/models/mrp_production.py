
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 15/10/2014
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

from openerp import models


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    def onchange_product(self, cr, uid, ids, product_id, context=None):
        if product_id:
            product_obj = self.pool['product.product']
            product = product_obj.browse(cr, uid, product_id, context)
            return {'value': {'product_uom': product.uom_id.id}}
