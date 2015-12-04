# -*- coding: utf-8 -*-
# (c) 2015 Daniel Campos - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    machines = fields.Many2many('machinery', 'machine_user_rel', 'user_id',
                                'machine_id', 'Machines')
