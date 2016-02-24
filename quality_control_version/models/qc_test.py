# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class QcTest(models.Model):
    _inherit = 'qc.test'

    version = fields.Integer(
        string='Version Number', default=0, readonly=True, copy=False)
    deactivate_date = fields.Date(string='Deactivated date', readonly=True)
    parent_test = fields.Many2one(
        comodel_name='qc.test', string='Parent Test', copy=False)
    old_versions = fields.One2many(
        comodel_name='qc.test', string='Old Versions',
        inverse_name='parent_test', context={'active_test': False})
    unrevisioned_name = fields.Char(
        string='Test Name', copy=True, readonly=True)

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            values['unrevisioned_name'] = values['name']
        return super(QcTest, self).create(values)

    @api.multi
    def write(self, values):
        for test in self:
            if 'name' in values and not values.get('version', test.version):
                values['unrevisioned_name'] = values['name']
            return super(QcTest, test).write(values)

    def _copy_test(self):
        new_test = self.copy({
            'version': self.version,
            'active': False,
            'deactivate_date': fields.Date.today(),
            'parent_test': self.id,
        })
        return new_test

    @api.multi
    def button_new_version(self):
        self.ensure_one()
        self._copy_test()
        revno = self.version
        self.write({
            'version': revno + 1,
            'name': '%s-%02d' % (self.unrevisioned_name, revno + 1)
        })

    @api.multi
    def action_open_older_versions(self):
        result = self.env.ref('quality_control.action_qc_test').read()[0]
        result['domain'] = [('id', 'in', self.old_versions.ids)]
        result['context'] = {'active_test': False}
        return result
