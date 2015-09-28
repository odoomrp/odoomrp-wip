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
        proc_obj = self.env['procurement.order']
        states = ('confirmed', 'exception')
        procurements = proc_obj._find_procurements_from_stock_planning(
            self.company, self.scheduled_date, states, product=self.product,
            warehouse=self.warehouse, location_id=self.location,
            without_purchases=True, without_productions=True, level=0)
        self.procurement_incoming_to_date = sum(
            procurements.mapped('product_qty'))
        procurements = proc_obj._find_procurements_from_stock_planning(
            self.company, self.scheduled_date, states, product=self.product,
            warehouse=self.warehouse, location_id=self.location,
            without_purchases=True, without_productions=True, level=1)
        self.procurement_plan_incoming_to_date = sum(
            procurements.mapped('product_qty'))
        self.scheduled_to_date = (
            self.qty_available + self.move_incoming_to_date +
            self.procurement_incoming_to_date + self.incoming_in_po -
            self.outgoing_to_date + self.incoming_in_mo -
            self.procurement_plan_incoming_to_date)

    procurement_plan_incoming_to_date = fields.Float(
        'Incoming up to date from procurements plan', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def _preparare_procurement_data_from_planning(self, line):
        vals = super(StockPlanning,
                     self)._preparare_procurement_data_from_planning(line)
        vals.update({'level': 1000})
        return vals
