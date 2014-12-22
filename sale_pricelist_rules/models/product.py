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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def show_pricelists(self):
        self.with_context(
            {'search_default_pricelist_type_id': 1}).browse(self.ids)
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.pricelist.item',
            'domain': [('product_tmpl_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'search_default_pricelist_type_id': 1}
            }


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def show_pricelists(self):
        self.with_context(
            {'search_default_pricelist_type_id': 1}).browse(self.ids)
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.pricelist.item',
            'domain': [('product_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            }
