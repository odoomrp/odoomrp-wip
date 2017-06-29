# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class StockPlanning(models.Model):

    _inherit = 'stock.planning'

    @api.one
    def _get_to_date(self):
        production_obj = self.env['mrp.production']
        proc_obj = self.env['procurement.order']
        super(StockPlanning, self)._get_to_date()
        states = ('confirmed', 'exception')
        procurements = proc_obj._find_procurements_from_stock_planning(
            self.company, self.scheduled_date, states=states,
            product=self.product, location_id=self.location,
            without_purchases=True, without_productions=True)
        self.procurement_incoming_to_date = sum(
            procurements.mapped('product_qty'))
        productions = production_obj._find_productions_from_stock_planning(
            self.company, self.scheduled_date, self.product, self.location)
        self.incoming_in_mo = sum(productions.mapped('product_qty'))
        productions = productions.filtered(
            lambda x: x.date_planned <= self.scheduled_date)
        if self.from_date:
            productions = productions.filtered(
                lambda x: x.date_planned >= self.from_date)
        self.productions = [(6, 0, productions.ids)]
        self.scheduled_to_date = (
            self.qty_available + self.procurement_incoming_to_date +
            self.incoming_in_po + + self.incoming_in_mo +
            self.move_incoming_to_date - self.outgoing_to_date)

    incoming_in_mo = fields.Float(
        'Incoming in MO', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    productions = fields.Many2many(
        comodel_name='mrp.production',
        relation='rel_stock_planning_mrp_production',
        column1='stock_planning_id', column2='production_id',
        string='MRP Productions', compute='_get_to_date')

    @api.multi
    def show_productions(self):
        self.ensure_one()
        return {'name': _('MRP Productions'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.productions.ids)]
                }
