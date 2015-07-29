# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, exceptions, _


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    capacity_per_cycle = fields.Float(
        string='Capacity per Cycle Max.', help='Capacity per cycle maximum.')
    capacity_per_cycle_min = fields.Float(
        string='Capacity per Cycle Min.', help='Capacity per cycle minimum.')

    @api.constrains('capacity_per_cycle', 'capacity_per_cycle_min')
    def _check_max_min(self):
        if (self.capacity_per_cycle <= 0.0 or
                self.capacity_per_cycle_min <= 0.0):
            raise exceptions.Warning(
                _('Capacity per cycle must be positive.'))
        if self.capacity_per_cycle < self.capacity_per_cycle_min:
            raise exceptions.Warning(
                _('Maximum value must be greater than minimum.'))


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    limited_production_capacity = fields.Boolean()

    @api.constrains('limited_production_capacity')
    def _check_one_limited_workcenter_per_route(self):
        if len(self.routing_id.workcenter_lines.filtered(
                'limited_production_capacity')) > 1:
            raise exceptions.Warning(
                _('Only one line must be defined as limited per routing.'))


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('product_qty', 'routing_id')
    def _calc_capacity(self):
        limited_lines = self.routing_id.workcenter_lines.filtered(
            'limited_production_capacity')
        self.capacity_min = limited_lines and min(limited_lines.mapped(
            'workcenter_id.capacity_per_cycle_min'))
        self.capacity_max = limited_lines and max(limited_lines.mapped(
            'workcenter_id.capacity_per_cycle'))
        self.show_split_button = (limited_lines and
                                  self.product_qty > self.capacity_max)

    show_split_button = fields.Boolean(
        'Show split button', compute='_calc_capacity')
    capacity_min = fields.Float(
        'Capacity min.', compute='_calc_capacity')
    capacity_max = fields.Float(
        'Capacity max.', compute='_calc_capacity')

    @api.multi
    @api.onchange('product_qty', 'routing_id')
    def _onchange_product_qty_check_capacity(self):
        self.ensure_one()
        result = {}
        if not self.product_qty or not self.routing_id:
            return result
        gt_max = self.capacity_max and self.product_qty > self.capacity_max
        lt_min = self.capacity_min and self.product_qty < self.capacity_min
        if gt_max and lt_min:
            warning = {
                'title': _('Warning!'),
                'message': _('Product QTY < Capacity per cycle'
                             ' minimum, and > Capacity per cycle'
                             ' maximum. You must click the'
                             ' "Split Quantity" button')
            }
            result['warning'] = warning
        elif lt_min:
            warning = {
                'title': _('Warning!'),
                'message': _('Product QTY < Capacity per cycle minimum.')
            }
            result['warning'] = warning
        elif gt_max:
            warning = {
                'title': _('Warning!'),
                'message': _('Product QTY > Capacity per cycle maximum.'
                             ' You must click the "Split Quantity" button')
            }
            result['warning'] = warning
        return result

    @api.one
    @api.onchange('routing_id')
    def _onchange_routing_id(self):
        limited = self.routing_id.workcenter_lines.filtered(
            'limited_production_capacity')
        if limited and limited.workcenter_id.capacity_per_cycle:
            self.product_qty = limited.workcenter_id.capacity_per_cycle

    @api.multi
    def button_split_quantity(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'mrp.production'
        return {
            'name': _('Split production'),
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.split.production',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }

    @api.multi
    def action_confirm(self):
        if any(p.show_split_button for p in self):
            raise exceptions.Warning(
                _('Product QTY > Capacity per cycle maximum. You must'
                  ' click the "Split Quantity" button'))
        return super(MrpProduction, self).action_confirm()


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    @api.onchange('workcenter_id')
    def _onchange_workcenter_id_check_capacity(self):
        result = {}
        if self.production_id.product_qty and self.workcenter_id:
            capacity_max = self.workcenter_id.capacity_per_cycle
            capacity_min = self.workcenter_id.capacity_per_cycle_min
            gt_max = (capacity_max and
                      self.production_id.product_qty > capacity_max)
            lt_min = (capacity_min and
                      self.production_id.product_qty < capacity_min)
            if lt_min or gt_max:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Product QTY < Capacity per cycle minimum, or'
                                 ' > Capacity per cycle maximum')
                }
                result['warning'] = warning
        return result
