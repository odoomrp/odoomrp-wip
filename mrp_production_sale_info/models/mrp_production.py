# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner = fields.Many2one(
        comodel_name='res.partner', string='Customer', store=True,
        related='move_prod_id.procurement_id.sale_line_id.order_id.partner_id')
    sale_order = fields.Many2one(
        comodel_name='sale.order', string='Sale Order', store=True,
        related='move_prod_id.procurement_id.sale_line_id.order_id')
    sale_line = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Line',
        related='move_prod_id.procurement_id.sale_line_id')
