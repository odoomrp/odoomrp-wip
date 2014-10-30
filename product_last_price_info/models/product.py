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

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_purchase_price = fields.Float(string='Last purchase price',
                                       readonly=True)
    last_purchase_date = fields.Date(string='Last purchase date',
                                     readonly=True)
    last_supplier_id = fields.Many2one('res.partner', string='Last Supplier',
                                       readonly=True)
    last_sale_price = fields.Float(string='Last sale price', readonly=True)
    last_sale_date = fields.Date(string='Last sale date', readonly=True)
    last_customer_id = fields.Many2one('res.partner', string='Last Customer',
                                       readonly=True)
