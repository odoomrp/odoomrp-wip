
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

from openerp import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        for product_tmpl in self:
            if 'uom_po_id' in vals:
                product_obj = self.env['product.product']
                st_mv_obj = self.env['stock.move']
                product_lst = product_obj.search([('product_tmpl_id', '=',
                                                   product_tmpl.id)])
                move = False
                for product in product_lst:
                    data_lst = st_mv_obj.search([('product_id', '=',
                                                  product.id)])
                    if data_lst:
                        move = True
                if move is False:
                    models.Model.write(self, vals)
        return super(ProductTemplate, self).write(vals)
