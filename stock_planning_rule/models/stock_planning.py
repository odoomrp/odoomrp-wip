# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class StockPlanning(models.Model):
    _inherit = 'stock.planning'

    @api.multi
    def _get_custom_rule(self):
        for planning in self:
            if planning.custom_stock_planning_rule:
                self._calculate_custom_rule(planning)

    def _calculate_custom_rule(self, planning):
        move_obj = self.env['stock.move']
        min = planning.company.stock_planning_min_days
        min = min * -1
        max = planning.company.stock_planning_max_days
        max = max * -1
        fdate = fields.Date.to_string(
            fields.Date.from_string(fields.Date.context_today(self)) +
            relativedelta(days=min))
        moves = move_obj._find_moves_from_stock_planning(
            planning.company, fields.Date.context_today(self), from_date=fdate,
            product=planning.product, location_id=planning.location)
        planning.custom_rule_min_qty = sum(
            moves.mapped('product_uom_qty'))
        fdate = fields.Date.to_string(
            fields.Date.from_string(fields.Date.context_today(self)) +
            relativedelta(days=max))
        moves = move_obj._find_moves_from_stock_planning(
            planning.company, fields.Date.context_today(self), from_date=fdate,
            product=planning.product, location_id=planning.location)
        planning.custom_rule_max_qty = sum(
            moves.mapped('product_uom_qty'))

    @api.one
    def _get_required_increase(self):
        self.required_increase = 0
        if not self.custom_stock_planning_rule:
            super(StockPlanning, self)._get_required_increase()
        else:
            self._get_required_increase_custom()

    def _get_required_increase_custom(self):
        self.required_increase = self.scheduled_to_date
        if (self.scheduled_to_date < 0 or
            (self.scheduled_to_date > 0 and self.custom_rule_min_qty == 0 and
             self.custom_rule_max_qty == 0)):
            self.required_increase = self.scheduled_to_date * -1
        if self.scheduled_to_date <= self.custom_rule_min_qty:
            if self.custom_rule_max_qty > self.scheduled_to_date:
                if self.scheduled_to_date >= 0:
                    self.required_increase = self.custom_rule_max_qty
                else:
                    self.required_increase = ((self.scheduled_to_date * -1) +
                                              self.custom_rule_max_qty)
        elif self.scheduled_to_date > 0:
            if (self.custom_rule_max_qty == 0 and
                    self.custom_rule_min_qty > self.scheduled_to_date):
                self.required_increase = (self.custom_rule_min_qty -
                                          self.scheduled_to_date)
            elif (self.custom_rule_max_qty > 0 and
                    self.scheduled_to_date > self.custom_rule_max_qty):
                self.required_increase = (
                    (self.scheduled_to_date - self.custom_rule_max_qty) *
                    (-1))
            else:
                self.required_increase = (
                    (self.scheduled_to_date - self.custom_rule_min_qty) *
                    (-1))

    custom_stock_planning_rule = fields.Boolean(
        string='customize min. qty, and max. qty rules',
        related='company.custom_stock_planning_rule')
    custom_rule_min_qty = fields.Float(
        'Custom rule min. qty', compute='_get_custom_rule',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    custom_rule_max_qty = fields.Float(
        'Custom rule max. qty', compute='_get_custom_rule',
        digits_compute=dp.get_precision('Product Unit of Measure'))
