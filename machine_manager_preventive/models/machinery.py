# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class Machinery(models.Model):
    _inherit = 'machinery'

    preventive_operations = fields.One2many(
        comodel_name='preventive.machine.operation',  inverse_name='machine',
        string='Next Revisions')
    repair_orders = fields.One2many(
        comodel_name='mrp.repair', inverse_name='idmachine',
        string='Preventive Repair Orders')
