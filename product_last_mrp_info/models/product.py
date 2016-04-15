# -*- coding: utf-8 -*-
# © 2014-2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_mrp_id = fields.Many2one(
        comodel_name='mrp.production', string='Last Manufacturing Order')
    last_mrp_cost = fields.Float(
        string='Last Manufacturing Order Cost',
        related='last_mrp_id.unit_real_cost')
    last_mrp_date = fields.Datetime(
        string='Last Manufacturing Order Date',
        related='last_mrp_id.date_finished')
