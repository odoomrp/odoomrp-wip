# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    proc_plan_level = fields.Integer(
        string='Procurement plan confirm level', default=-1,
        help='Level of procurement orders to be executed, when creating the '
        'procurement plan from the sale order. If field value < 0, the'
        ' procurements of procurement plan were not confirmed.')
