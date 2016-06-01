# -*- coding: utf-8 -*-
# (c) 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    is_repair_cost = fields.Boolean('Is repair cost')
