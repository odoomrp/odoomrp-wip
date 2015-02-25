# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    @api.one
    def _count_confirmed_pickings(self):
        self.num_confirmed = sum(1 for x in self.picking_ids if x.state ==
                                 'confirmed')

    @api.one
    def _count_assigned_pickings(self):
        self.num_assigned = sum(1 for x in self.picking_ids if x.state ==
                                'assigned')

    pickings_products = fields.One2many(
        'stock.move', 'wave', string='Products', readonly=True)
    pickings_operations = fields.One2many(
        'stock.pack.operation', 'wave', string='Operations', readonly=True)
    num_confirmed = fields.Integer(
        compute="_count_confirmed_pickings", string="Confirmed pickings")
    num_assigned = fields.Integer(
        compute="_count_assigned_pickings", string="Assigned pickings")

    @api.one
    def button_check_disponibility(self):
        picking_obj = self.env['stock.picking']
        picking_ids = [picking.id for picking in
                       self.picking_ids if picking.state == 'confirmed']
        pickings = picking_obj.browse(picking_ids)
        pickings.action_assign()

    def action_transfer(self, cr, uid, ids, context=None):
        picking_obj = self.pool['stock.picking']
        wave = self.browse(cr, uid, ids[0], context=context)
        picking_ids = [picking.id for picking in
                       wave.picking_ids if picking.state == 'assigned']
        return  picking_obj.do_enter_transfer_details(
            cr, uid, picking_ids, context=context)


class StockMove(models.Model):
    _inherit = 'stock.move'

    wave = fields.Many2one('stock.picking.wave', related='picking_id.wave_id',
                           string='Picking Wave', store=True)
