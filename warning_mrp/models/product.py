# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models
from openerp.addons.warning.warning import WARNING_MESSAGE, WARNING_HELP


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_production_warn = fields.Selection(
        selection=WARNING_MESSAGE, string='Manufacturing Order',
        help=WARNING_HELP, required=True, default='no-message')
    mrp_production_warn_msg = fields.Text(
        string='Message for Manufacturing Order')
