# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    def make_claim_from_inspection_line(self, line, categ):
        corrective_obj = self.env['crm.claim.corrective']
        action_obj = self.env['crm.claim.corrective.action']
        claim = super(QcInspection, self).make_claim_from_inspection_line(
            line, categ)
        if line.tolerance_status == 'not_tolerable':
            corrective = corrective_obj.create({'claim_id': claim.id})
            vals = {'name': 'NC',
                    'sol_claim_id': claim.id,
                    'corrective_action_id': corrective.id}
            action_obj.create(vals)
            claim.update({'aaccseq': corrective.id})
        return claim
