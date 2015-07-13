# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    def action_button_confirm(self):
        procurement_obj = self.env['procurement.order']
        res = super(SaleOrder, self).action_button_confirm()
        for line in self.order_line:
            routes = line.product_id.route_ids.filtered(
                lambda r: r.name in ('Make To Order', 'Buy'))
            if line.product_id.type == 'service' and len(routes) == 2:
                vals = {'name': self.name + ' - ' + line.product_id.name,
                        'origin': self.name,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty
                        }
                proc_vals = procurement_obj.onchange_product_id(
                    line.product_id.id)
                if 'value' not in proc_vals:
                    raise exceptions.Warning(
                        _('Product UOM or Product UOS not found for product:'
                          ' %s') % (line.product_id.name))
                vals.update(proc_vals['value'])
                proc = procurement_obj.create(vals)
                proc.write(
                    {'rule_id': procurement_obj._find_suitable_rule(proc)})
        return res
