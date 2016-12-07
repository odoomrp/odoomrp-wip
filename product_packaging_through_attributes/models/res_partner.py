# -*- coding: utf-8 -*-
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit',
    )
