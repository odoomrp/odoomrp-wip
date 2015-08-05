# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockPlanning(models.Model):
    _inherit = 'stock.planning'

    @api.one
    def _get_to_date(self):
        super(StockPlanning, self)._get_to_date()
        procurement_obj = self.env['procurement.order']
        self.procurement_plan_incoming_to_date = 0
        cond = [('company_id', '=', self.company.id),
                ('product_id', '=', self.product.id),
                ('date_planned', '<=', self.scheduled_date),
                ('location_id', '=', self.location.id),
                ('level', '>', 1),
                ('state', 'in', ('confirmed', 'running'))]
        if self.from_date:
            cond.append(('date_planned', '>', self.from_date))
        procurements = procurement_obj.search(cond)
        self.procurement_plan_incoming_to_date = sum(
            x.product_qty for x in procurements)
        if self.scheduled_to_date and self.procurement_plan_incoming_to_date:
            self.scheduled_to_date -= self.procurement_plan_incoming_to_date

    procurement_plan_incoming_to_date = fields.Float(
        'Incoming up to date from procurements plan', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
