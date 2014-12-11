# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    external = fields.Boolean('External', help="Is Subcontract Operation")
    semifinished_id = fields.Many2one(
        'product.product', 'Semifinished Subcontracting',
        domain=[('type', '=', 'product'),
                # ('route_ids','in', ['ref(purchase.route_warehouse0_buy)',
                #                    'ref(stock.route_warehouse0_mto)'])
                ])
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      domain=[('code', '=', 'outgoing')])
    virtual_subcontracting_location_id = fields.Many2one(
        'stock.location', 'Virtual Subcontrating Location')
    out_subcontracting_location_id = fields.Many2one(
        'stock.location', 'Consumption Subcontrating Location')
    in_subcontracting_location_id = fields.Many2one(
        'stock.location', 'Destination Subcontrating Location')


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    out_picking_id = fields.Many2one('stock.picking', 'Out Picking')
    in_picking_id = fields.Many2one('stock.picking', 'In Picking')

    @api.model
    def create(self, vals):
        wc_line = super(MrpProductionWorkcenterLine, self).create(vals)
        if wc_line.routing_wc_line.external:
            routing_wc = wc_line.routing_wc_line
            vals = {'name': wc_line.name,
                    'origin': wc_line.name,
                    # 'group_id': fields.many2one('procurement.group'
                    # 'rule_id': fields.many2one('procurement.rule'
                    'product_id': routing_wc.semifinished_id.id,
                    'product_qty': wc_line.qty,
                    'product_uom': wc_line.uom.id,
                    # 'product_uos_qty': fields.float('UoS Quantity'
                    # 'product_uos': fields.many2one('product.uom'
                    'location_id':
                        routing_wc.in_subcontracting_location_id.id,
                    }
            self.env['procurement.order'].create(vals)
        return wc_line


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        if self.routing_id:
            for wc_line in self.routing_id.workcenter_lines:
                if wc_line.external:
                    pass
        return res
