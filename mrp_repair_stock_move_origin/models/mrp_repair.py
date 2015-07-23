# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.multi
    def action_repair_done(self):
        res = super(MrpRepair, self).action_repair_done()
        for repair_id in set(res.keys()):
            repair = self.browse(repair_id)
            for repair_line in repair.operations:
                repair_line.move_id.origin = repair.name
        return res
