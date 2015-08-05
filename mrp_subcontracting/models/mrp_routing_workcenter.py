# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    external = fields.Boolean('External', help="Is Subcontract Operation")
    semifinished_id = fields.Many2one(
        comodel_name='product.product', string='Semifinished Subcontracting')
