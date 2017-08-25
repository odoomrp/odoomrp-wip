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
        super(StockPlanning, self)._get_to_date()
        proc_obj = self.env['procurement.order']
        move_obj = self.env['stock.move']
        reservation_obj = self.env['stock.reservation']
        moves = move_obj._find_moves_from_stock_planning(
            self.company, self.scheduled_date, product=self.product,
            location_id=self.location, without_reservation=True)
        self.outgoing_to_date = sum(moves.mapped('product_uom_qty'))
        if self.from_date:
            moves = moves.filtered(lambda x: x.date >= self.from_date)
        self.outgoing_to_date_moves = [(6, 0, moves.ids)]
        moves = move_obj._find_moves_from_stock_planning(
            self.company, self.scheduled_date, product=self.product,
            location_id=self.location, location_dest_id=self.env.ref(
                'stock_reserve.stock_location_reservation'))
        self.outgoing_to_date_reserve_destination = sum(
            moves.mapped('product_uom_qty'))
        states = ('confirmed', 'exception')
        procurements = proc_obj._find_procurements_from_stock_planning(
            self.company, self.scheduled_date, states=states,
            product=self.product, location_id=self.location,
            without_purchases=True, without_productions=True, level=0)
        self.procurement_incoming_to_date = sum(
            procurements.mapped('product_qty'))
        procurements = proc_obj._find_procurements_from_stock_planning(
            self.company, self.scheduled_date, states=states,
            product=self.product, location_id=self.location,
            without_purchases=True, without_productions=True, level=1)
        self.procurement_plan_incoming_to_date_levelgreater0 = sum(
            procurements.mapped('product_qty'))
        self.scheduled_to_date = (
            self.qty_available + self.procurement_incoming_to_date +
            self.procurement_plan_incoming_to_date_levelgreater0 +
            self.incoming_in_po + self.incoming_in_mo +
            self.move_incoming_to_date - self.outgoing_to_date -
            self.outgoing_to_date_reserve_destination)
        reservations = reservation_obj._find_reservations_from_stock_planning(
            self.company, self.from_date, self.scheduled_date, self.product,
            self.location,
            self.env.ref('stock_reserve.stock_location_reservation'))
        self.reservations = [(6, 0, reservations.ids)]

    procurement_plan_incoming_to_date_levelgreater0 = fields.Float(
        'Incoming up to date from procurements plan level greater than 0',
        compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    outgoing_to_date_reserve_destination = fields.Float(
        'Outgoing to date reserve destination', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    reservations = fields.Many2many(
        comodel_name='stock.reservation',
        relation='rel_stock_planning_stock_reservation',
        column1='stock_planning_id', column2='stock_reservation_id',
        string='Reservations', compute='_get_to_date')

    @api.multi
    def _preparare_procurement_data_from_planning(self, line):
        vals = super(StockPlanning,
                     self)._preparare_procurement_data_from_planning(line)
        vals.update({'level': 1000})
        return vals

    @api.multi
    def show_reservations(self):
        self.ensure_one()
        return {'name': _('Resevations'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'stock.reservation',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.reservations.ids)]
                }
