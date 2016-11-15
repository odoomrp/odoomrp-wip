# -*- coding: utf-8 -*-
# (c) 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    preventive_operations = fields.Many2many(
        comodel_name='preventive.machine.operation')
    idmachine = fields.Many2one(comodel_name='machinery', string='Machine')
    preventive = fields.Boolean(string='Is preventive')

    @api.multi
    def action_repair_end(self):
        res = super(MrpRepair, self).action_repair_end()
        for record in self:
            if record.preventive:
                for preventive in record.preventive_operations:
                    if preventive.update_preventive == 'after_repair':
                        preventive._next_action_update()
        return res
