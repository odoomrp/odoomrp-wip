# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestQualityControlVersion(common.TransactionCase):

    def setUp(self):
        super(TestQualityControlVersion, self).setUp()
        self.test_model = self.env['qc.test']
        self.quality_test = self.browse_ref('quality_control.qc_test_1')

    def test_post_init(self):
        tests = self.test_model.search([])
        for test in tests:
            self.assertTrue(test.unrevisioned_name)

    def test_versioning(self):
        self.assertEquals(self.quality_test.name,
                          self.quality_test.unrevisioned_name)
        version = self.quality_test.version
        self.quality_test.button_new_version()
        self.assertEquals(self.quality_test.version,
                          version + 1)
        self.assertEquals(
            '%s-%02d' % (self.quality_test.unrevisioned_name,
                         self.quality_test.version), self.quality_test.name)
        for old_test in self.quality_test.old_versions:
            if old_test.version:
                self.assertEquals(
                    '%s-%02d' % (old_test.unrevisioned_name, old_test.version),
                    old_test.name)
            self.assertEquals(self.quality_test.unrevisioned_name,
                              old_test.unrevisioned_name)
            self.assertTrue(old_test.version < self.quality_test.version)
