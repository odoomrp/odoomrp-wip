# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
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

    show_split_button = fields.Boolean('Show split button', default=False)
    capacity_min = fields.Integer('Capacity min.')
    capacity_max = fields.Integer('Capacity max.')

    @api.multi
    def product_qty_change_production_capacity(self, product_qty=0,
                                               routing_id=False):
        result = {'value': {'show_split_button': False}}
        routing_obj = self.env['mrp.routing']
        if product_qty and routing_id:
            routing = routing_obj.browse(routing_id)
            for line in routing.workcenter_lines:
                if line.limited_production_capacity:
                    capacity_min = (
                        line.workcenter_id.capacity_per_cycle_min or
                        sys.float_info.min)
                    capacity_max = (line.workcenter_id.capacity_per_cycle or
                                    sys.float_info.max)
                    if capacity_min and product_qty < capacity_min:
                        warning = {
                            'title': _('Warning!'),
                            'message': _('Product QTY < Capacity per cycle'
                                         ' minimun')
                        }
                        result['warning'] = warning
                    else:
                        if capacity_max and product_qty > capacity_max:
                            self.show_split_button = True
                            warning = {
                                'title': _('Warning!'),
                                'message': _('Product QTY > Capacity per cycle'
                                             ' maximun. You must press the'
                                             ' "Split Quantity" button')
                            }
                            result['warning'] = warning
                            vals = {'show_split_button': True,
                                    'capacity_min': capacity_min,
                                    'capacity_max': capacity_max}
                            result['value'].update(vals)
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
        context['product_qty'] = self.product_qty
        context['capacity_min'] = self.capacity_min
        context['capacity_max'] = self.capacity_max
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
                                     ' minimun, or > Capacity per'
                                     ' cycle maximun')
                    }
                    result['warning'] = warning
        return result
