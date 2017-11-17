# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestCrmClaimCorrective(TransactionCase):

    def setUp(self):
        super(TestCrmClaimCorrective, self).setUp()
        self.ir_sequence_model = self.env['ir.sequence']
        self.corrective_model = self.env['crm.claim.corrective']
        self.sequence = self.browse_ref(
            'crm_claim_corrective.crm_claim_corrective_seq')

    def test_new_code_assign(self):
        code = self._get_next_code()
        corrective = self.corrective_model.create({
            'name': 'Testing code',
        })
        self.assertNotEqual(corrective.code, '/')
        self.assertEqual(corrective.code, code)

    def _get_next_code(self):
        d = self.ir_sequence_model._interpolation_dict()
        prefix = self.ir_sequence_model._interpolate(
            self.sequence.prefix, d)
        suffix = self.ir_sequence_model._interpolate(
            self.sequence.suffix, d)
        code = (prefix + ('%%0%sd' % self.sequence.padding %
                          self.sequence.number_next_actual) + suffix)
        return code
