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

    @api.model
    def create(self, values):
        bom = super(MrpBom, self).create(values)
        if bom.product_tmpl_id:
            bom.code = bom.product_tmpl_id.reference_mask
        elif bom.product_id:
            bom.code = bom.product_id.default_code
        return bom

    @api.one
    def write(self, values):
        product_obj = self.env['product.product']
        template_obj = self.env['product.template']
        if values.get('product_tmpl_id'):
            product_tmpl = template_obj.browse(values.get('product_tmpl_id'))
            values['code'] = product_tmpl.reference_mask
        elif values.get('product_id'):
            product = product_obj.browse(values.get('product_id'))
            values['code'] = product.default_code
        return super(MrpBom, self).write(values)
