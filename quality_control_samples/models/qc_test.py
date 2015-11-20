# -*- coding: utf-8 -*-
# (c) 2014-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class QcTest(models.Model):
    _inherit = "qc.test"

    sample = fields.Many2one(
        comodel_name="qc.sample", string="Sample definition")
