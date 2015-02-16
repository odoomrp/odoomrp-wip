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


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_second_discount = fields.Boolean(
        string='Allow second discount',
        implied_group='product_pricelist_rules.group_second_discount')
    group_third_discount = fields.Boolean(
        string='Allow third discount',
        implied_group='product_pricelist_rules.group_third_discount')

    @api.one
    @api.onchange('group_second_discount', 'group_third_discount')
    def onchange_group_discount(self):
        if self.group_third_discount:
            self.group_discount_per_so_line = True
            self.group_second_discount = True
        elif self.group_second_discount:
            self.group_discount_per_so_line = True

    @api.multi
    def write(self, vals):
        if vals.get('group_third_discount'):
            vals['group_second_discount'] = True
            vals['group_discount_per_so_line'] = True
        elif vals.get('group_second_discount'):
            vals['group_discount_per_so_line'] = True
        return super(SaleConfigSettings, self).write(vals)
