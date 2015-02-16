# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.one
    @api.depends('user')
    def _get_user_department(self):
        if self.user:
            self.department = (self.user.employee_ids and
                               self.user.employee_ids[0].department_id)

    department = fields.Many2one(
        comodel_name='hr.department', string='Department',
        compute='_get_user_department', readonly=True, store=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    user = fields.Many2one(
        comodel_name='res.users', related='inspection_id.user')
    department = fields.Many2one(
        comodel_name='hr.department', related='inspection_id.department')
