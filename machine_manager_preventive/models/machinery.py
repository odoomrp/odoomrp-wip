# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class Machinery(models.Model):
    _inherit = 'machinery'

    preventive_operations = fields.One2many(
        'preventive.machine.operation',  'machine', 'Next Revisions')
    repair_orders = fields.One2many('mrp.repair', 'idmachine',
                                    'Preventive Repair Orders')
