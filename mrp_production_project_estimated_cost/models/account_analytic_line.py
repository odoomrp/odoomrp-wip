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
from openerp import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.one
    @api.depends('product_id')
    def _estim_standard_cost(self):
        self.estim_standard_cost = self.product_id.standard_price

    @api.one
    @api.depends('product_id')
    def _estim_average_cost(self):
        self.estim_average_cost = self.product_id.standard_price

    @api.one
    @api.depends('product_id')
    def _last_purchase_cost(self):
        self.last_purchase_cost = 0
        if self.product_id:
            self.last_purchase_cost = self.product_id.last_purchase_price

    @api.one
    @api.depends('product_id')
    def _last_sale_price(self):
        self.last_sale_price = 0
        if self.product_id:
            self.last_sale_price = self.product_id.last_sale_price

    estim_standard_cost = fields.Float(
        string='Estimate Standard Cost', compute='_estim_standard_cost',
        store=True)
    estim_average_cost = fields.Float(
        string='Estimate Average Cost', compute='_estim_average_cost',
        store=True)
    last_purchase_cost = fields.Float(
        string='Last Purchase Cost', compute='_last_purchase_cost',
        store=True)
    last_sale_price = fields.Float(
        string='Last Sale Price', compute='_last_sale_price',
        store=True)
