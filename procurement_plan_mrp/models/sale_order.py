# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_ship_create(self):
        result = super(SaleOrder, self).action_ship_create()
        for order in self:
            for line in order.order_line:
                if (self.env.ref('mrp.route_warehouse0_manufacture').id in
                        line.product_id.route_ids.ids):
                    line._find_mrp_procurement_with_level0()
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    def _find_mrp_procurement_with_level0(self):
        proc_obj = self.env['procurement.order']
        cond = [('sale_line_id', '=', self.id)]
        procurement = proc_obj.search(cond, limit=1)
        if procurement:
            cond = [('id', '!=', procurement.id),
                    ('group_id', '=', procurement.group_id.id),
                    ('product_id', '=', procurement.product_id.id),
                    ('product_qty', '=', self.product_uom_qty),
                    ('production_id', '!=', False),
                    ('plan', '=', False),
                    ('level', '=', 0)]
            procurement = proc_obj.search(cond, limit=1)
            if procurement:
                procurement._create_procurement_plan_from_procurement(
                    self.order_id)
