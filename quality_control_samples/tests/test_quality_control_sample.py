# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestQualityControlSample(TransactionCase):

    def setUp(self):
        super(TestQualityControlSample, self).setUp()
        self.test = self.env.ref('quality_control.qc_test_1')
        self.sample = self.env.ref('quality_control_samples.qc_sample_normal')

    def test_samples_ranks(self):
        self.assertEqual(self.sample.get_samples_number(3), 1)
        self.assertEqual(self.sample.get_samples_number(15), 2)
        self.assertEqual(self.sample.get_samples_number(28), 3)
        self.assertEqual(self.sample.get_samples_number(32), 4)

    def test_samples_from_set_test_wizard(self):
        inspection = self.env['qc.inspection'].create({
            'name': 'Test Inspection',
            'qty': 25,
        })
        wizard = self.env['qc.inspection.set.test'].with_context(
            active_id=inspection.id).create({'test': self.test.id})
        wizard.action_create_test()
        self.assertEqual(len(inspection.inspection_lines), 6)
