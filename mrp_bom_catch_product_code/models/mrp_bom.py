# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def onchange_product_tmpl_id(self, product_tmpl_id, product_qty=0):
        res = super(MrpBom, self).onchange_product_tmpl_id(
            product_tmpl_id, product_qty=product_qty)
        if product_tmpl_id:
            product_tmpl = self.env['product.template'].browse(product_tmpl_id)
            res['value'].update({'code': product_tmpl.default_code})
        return res

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.code = self.product_id.default_code
