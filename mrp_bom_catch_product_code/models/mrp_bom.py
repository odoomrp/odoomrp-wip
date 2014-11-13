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

    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id,
                                 product_qty=0, context=None):
        template_obj = self.pool['product.template']
        res = super(MrpBom, self).onchange_product_tmpl_id(
            cr, uid, ids, product_tmpl_id=product_tmpl_id,
            product_qty=product_qty, context=context)
        if res.get('value') and product_tmpl_id:
            value = res.get('value')
            template = template_obj.browse(cr, uid, product_tmpl_id,
                                           context=context)
            if not template.attribute_value_ids:
                value.update({'code': template.default_code})
                res.update({'value': value})
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.code = self.product_id.default_code
