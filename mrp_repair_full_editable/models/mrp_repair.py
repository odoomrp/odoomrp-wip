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

from openerp import models, fields, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    fees_lines = fields.One2many(readonly=False)
    operations = fields.One2many(readonly=False)
    invoice_method = fields.Selection(readonly=False)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self, product_id=None):
        res = super(MrpRepair, self).onchange_product_id(product_id)
        if not self.partner_id:
            res['value']['pricelist_id'] = self.env.ref('product.list0')
        return res
