# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# (c) 2015 Esther Martín <esthermartin@avanzosc.es> - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    machine_ok = fields.Boolean('Can be a Machine', help="Determines if the "
                                "product is related with a machine.")


class ProductProduct(models.Model):
    _inherit = "product.product"

    machines = fields.One2many(
        string='Machines', comodel_name='machinery',
        inverse_name='product')
    machine_count = fields.Integer(
        compute='_compute_machines', string='Machines')

    @api.multi
    @api.depends('machines')
    def _compute_machines(self):
        for product in self:
            product.machine_count = len(product.machines)
