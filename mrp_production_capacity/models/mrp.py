# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
import sys


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    capacity_per_cycle = fields.Float(
        string='Capacity per Cycle Max.', help='Capacity per cycle maximum.')
    capacity_per_cycle_min = fields.Float(
        string='Capacity per Cycle Min.', help='Capacity per cycle minimum.')


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    limited_production_capacity = fields.Boolean()


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('product_qty', 'routing_id')
    def _calc_capacity(self):
        self.show_split_button = False
        self.capacity_min = 0
        self.capacity_max = 0
        if self.product_qty and self.routing_id:
            max = 0
            min = 0
            for line in self.routing_id.workcenter_lines:
                if line.limited_production_capacity:
                    capacity_min = (
                        line.workcenter_id.capacity_per_cycle_min or
                        sys.float_info.min)
                    capacity_max = (line.workcenter_id.capacity_per_cycle or
                                    sys.float_info.max)
                    if capacity_min and self.product_qty < capacity_min:
                        if not min:
                            min = capacity_min
                        else:
                            if capacity_min > min:
                                min = capacity_min
                    if capacity_max and self.product_qty > capacity_max:
                        if not max:
                            max = capacity_max
                        else:
                            if capacity_max < max:
                                max = capacity_max
            self.capacity_min = min
            self.capacity_max = max
            if max and self.product_qty > max:
                self.show_split_button = True

    show_split_button = fields.Boolean(
        'Show split button', default=False, compute='_calc_capacity')
    capacity_min = fields.Integer(
        'Capacity min.', default=0, compute='_calc_capacity')
    capacity_max = fields.Integer(
        'Capacity max.', default=0, compute='_calc_capacity')

    @api.multi
    def product_qty_change_production_capacity(self, product_qty=0,
                                               routing_id=False):
        result = {}
        if product_qty and routing_id:
            routing = self.env['mrp.routing'].browse(routing_id)
            max = 0
            min = 0
            for line in routing.workcenter_lines:
                if line.limited_production_capacity:
                    capacity_min = (
                        line.workcenter_id.capacity_per_cycle_min or
                        sys.float_info.min)
                    capacity_max = (line.workcenter_id.capacity_per_cycle or
                                    sys.float_info.max)
                    if capacity_min and product_qty < capacity_min:
                        if not min:
                            min = capacity_min
                        else:
                            if capacity_min > min:
                                min = capacity_min
                    if capacity_max and product_qty > capacity_max:
                        if not max:
                            max = capacity_max
                        else:
                            if capacity_max < max:
                                max = capacity_max
            if max and min:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Product QTY < Capacity per cycle'
                                 ' minimum, and > Capacity per cycle'
                                 ' maximum. You must click the'
                                 ' "Split Quantity" button')
                }
                result['warning'] = warning
            elif min:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Product QTY > Capacity per cycle maximum.'
                                 ' You must click the "Split Quantity" button')
                }
                result['warning'] = warning
            elif max:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Product QTY > Capacity per cycle maximum.'
                                 ' You must click the "Split Quantity" button')
                }
                result['warning'] = warning
        return result

    @api.one
    @api.onchange('routing_id')
    def onchange_routing(self):
        if self.routing_id:
            for line in self.routing_id.workcenter_lines:
                if (line.limited_production_capacity and
                        line.workcenter_id.capacity_per_cycle):
                    self.product_qty = line.workcenter_id.capacity_per_cycle

    @api.multi
    def button_split_quantity(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'mrp.production'
        return {'name': _('Split production'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.split.production',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': context
                }

    @api.multi
    def action_confirm(self):
        for production in self:
            if production.show_split_button:
                raise exceptions.Warning(
                    _('Product QTY > Capacity per cycle maximum. You must'
                      ' click the "Split Quantity" button'))
        return super(MrpProduction, self).action_confirm()


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    def workcenter_change_production_capacity(self, product_qty=0,
                                              workcenter_id=False):
        result = {}
        result['value'] = {}
        workcenter_obj = self.env['mrp.workcenter']
        if product_qty and workcenter_id:
            workcenter = workcenter_obj.browse(workcenter_id)
            capacity_min = (workcenter.capacity_per_cycle_min or
                            sys.float_info.min)
            capacity_max = (workcenter.capacity_per_cycle or
                            sys.float_info.max)
            if capacity_min and capacity_max:
                if (product_qty < capacity_min or
                        product_qty > capacity_max):
                    warning = {
                        'title': _('Warning!'),
                        'message': _('Product QTY < Capacity per cycle'
                                     ' minimum, or > Capacity per'
                                     ' cycle maximum')
                    }
                    result['warning'] = warning
        return result
