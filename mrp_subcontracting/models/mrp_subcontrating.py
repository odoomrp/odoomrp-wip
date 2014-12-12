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
from openerp import models, fields, api, exceptions, _


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


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    external = fields.Boolean(related='routing_wc_line.external', store=True,
                              readonly=True, copy=False)
    purchase_order = fields.Many2one('purchase.order', 'Purchase Order')
    out_picking = fields.Many2one('stock.picking', 'Out Picking')
    in_picking = fields.Many2one('stock.picking', 'In Picking')
    procurement_order = fields.Many2one('procurement.order',
                                        'Procurement Order')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    def _created_purchases(self):
        purchase_obj = self.env['purchase.order']
        cond = [('mrp_production', '=', self.id)]
        purchases = purchase_obj.search(cond)
        cont = 0
        for purchase in purchases:
            cont += 1
        self.created_purchases = cont

    def _created_outpickings(self):
        picking_obj = self.env['stock.picking']
        cond = [('mrp_production', '=', self.id)]
        pickings = picking_obj.search(cond)
        cont = 0
        for picking in pickings:
            if picking.picking_type_id.code == 'outgoing':
                cont += 1
        self.created_outpickings = cont

    def _created_inpickings(self):
        picking_obj = self.env['stock.picking']
        cond = [('mrp_production', '=', self.id)]
        pickings = picking_obj.search(cond)
        cont = 0
        for picking in pickings:
            if picking.picking_type_id.code == 'incoming':
                cont += 1
        self.created_inpickings = cont

    created_purchases = fields.Integer(
        string='Created Purchases', readonly=True,
        compute='_created_purchases', track_visibility='always')
    created_outpickings = fields.Integer(
        string='Created Out Pickings', readonly=True,
        compute='_created_outpickings', track_visibility='always')
    created_inpickings = fields.Integer(
        string='Created In Pickings', readonly=True,
        compute='_created_inpickings', track_visibility='always')

    @api.one
    def action_confirm(self):
        user_obj = self.env['res.users']
        rule_obj = self.env['procurement.rule']
        warehouse_obj = self.env['stock.warehouse']
        res = super(MrpProduction, self).action_confirm()
        user = user_obj.browse(self._uid)
        cond = [('company_id', '=', user.company_id.id)]
        warehouse = False
        for workcenter in self.routing_id.workcenter_lines:
            if workcenter.external:
                created_procurement = False
                if not warehouse:
                    cond = [('company_id', '=', user.company_id.id)]
                    warehouse = warehouse_obj.search(cond, limit=1)
                    if not warehouse:
                        raise exceptions.Warning(
                            _('Production Confirmation Error'),
                            _('Company warehouse not found'))
                    cond = [('warehouse_id', '=', warehouse.id),
                            ('action', '=', 'buy')]
                    rule = rule_obj.search(cond, limit=1)
                    if not rule:
                        raise exceptions.Warning(
                            _('Production Confirmation Error'),
                            _('Rule for procurement order not found'))
                for move in self.move_lines:
                    if (move.work_order.routing_wc_line.id == workcenter.id and
                            not created_procurement):
                        created_procurement = True
                        self._create_external_procurement(move, warehouse,
                                                          rule)
        return res

    def _create_external_procurement(self, move, warehouse, rule):
        procurement_obj = self.env['procurement.order']
        wc_line = move.work_order.routing_wc_line
        ptype = wc_line.picking_type_id
        move.update({'location_id':
                     ptype.default_location_src_id.id,
                     'location_dest_id':
                     ptype.default_location_dest_id.id})
        vals = {'name': move.work_order.name,
                'origin': move.work_order.name,
                'product_id': wc_line.semifinished_id.id,
                'product_qty': self.product_qty,
                'product_uom': wc_line.semifinished_id.uom_id.id,
                'location_id': ptype.default_location_src_id.id,
                'production_id': self.id,
                'warehouse_id': warehouse.id,
                'rule_id': rule.id,
                'mrp_operation': move.work_order.id,
                }
        procurement = procurement_obj.create(vals)
        procurement.run()
        vals_workorder = {'procurement_order': procurement.id}
        move.work_order.update(vals_workorder)
        return True
