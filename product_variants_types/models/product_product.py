# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import models


class ProductProduct(models.Model):
    # Redefine again the inheritance due to
    # https://github.com/odoo/odoo/issues/9084. This won't be needed on v10
    _inherit = ['product.product', 'product.configurator']
    _name = "product.product"
