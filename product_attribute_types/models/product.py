# -*- coding: utf-8 -*-
# Copyright 2014-2016 Mikel Arregui - AvanzOSC
# Copyright 2014-2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    attr_type = fields.Selection(
        required=True,
        string="Type",
        default='select',
        selection=[
            ('select', 'Select'),
            ('range', 'Range'),
            ('numeric', 'Numeric')
        ],
    )


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"

    required = fields.Boolean('Required')
    default = fields.Many2one('product.attribute.value', 'Default')
    attr_type = fields.Selection(string='Type', store=False,
                                 related='attribute_id.attr_type')


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    attr_type = fields.Selection(string='Type',
                                 related='attribute_id.attr_type')
    numeric_value = fields.Float('Numeric Value', digits=(12, 6))
    min_range = fields.Float('Min', digits=(12, 6))
    max_range = fields.Float('Max', digits=(12, 6))
