# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import fields, models


class ProductAttributePrice(models.Model):
    _inherit = 'product.attribute.price'

    attribute_id = fields.Many2one(
        comodel_name='product.attribute', related='value_id.attribute_id')
