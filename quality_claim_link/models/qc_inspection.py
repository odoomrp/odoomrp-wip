# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    automatic_claims = fields.Boolean('Automatic Claims', default=False)
    claims = fields.One2many(
        comodel_name='crm.claim', inverse_name='inspection_id',
        string='Claims')

    @api.multi
    def set_test(self, test, force_fill=False):
        super(QcInspection, self).set_test(test, force_fill)
        for inspection in self:
            inspection.automatic_claims = test.automatic_claims

    @api.multi
    def action_approve(self):
        super(QcInspection, self).action_approve()
        for inspection in self:
            if inspection.state == 'failed':
                inspection.make_claim_from_inspection()

    def make_claim_from_inspection(self):
        crm_claim_obj = self.env['crm.claim']
        crm_claim = crm_claim_obj.create({
            'name': _('Quality test %s for product %s unsurpassed') % (
                self.name, self.object_id.name),
            'date': fields.Datetime.now(),
            'ref': '%s,%s' % (self.object_id._model, self.object_id.id),
            'inspection_id': self.id})
