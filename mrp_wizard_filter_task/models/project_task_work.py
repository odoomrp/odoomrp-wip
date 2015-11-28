# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProjectTaskWork(models.Model):
    _inherit = 'project.task.work'

    mrp_production_id = fields.Many2one(
        'mrp.production', string='Manufacturing Order', store=True,
        related='task_id.mrp_production_id')
    wk_order = fields.Many2one(
        'mrp.production.workcenter.line', string='Work Order', store=True,
        related='task_id.workorder')
