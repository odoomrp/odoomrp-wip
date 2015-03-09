# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    @api.one
    def _count_confirmed_pickings(self):
        self.num_confirmed = len(self.picking_ids.filtered(lambda x: x.state ==
                                                           'confirmed'))

    @api.one
    def _count_assigned_pickings(self):
        self.num_assigned = len(self.picking_ids.filtered(lambda x: x.state ==
                                                          'assigned'))

    pickings_products = fields.One2many(
        'stock.move', 'wave', string='Products', readonly=True)
    pickings_operations = fields.One2many(
        'stock.pack.operation', 'wave', string='Operations', readonly=True)
    num_confirmed = fields.Integer(
        compute="_count_confirmed_pickings", string="Confirmed pickings")
    num_assigned = fields.Integer(
        compute="_count_assigned_pickings", string="Assigned pickings")
    partner = fields.Many2one('res.partner', 'Partner')

    @api.one
    def button_check_availability(self):
        picking_obj = self.env['stock.picking']
        picking_ids = [picking.id for picking in
                       self.picking_ids if picking.state == 'confirmed']
        pickings = picking_obj.browse(picking_ids)
        pickings.action_assign()

    # The old API is used because the father is updated method context
    def action_transfer(self, cr, uid, ids, context=None):
        picking_obj = self.pool['stock.picking']
        wave = self.browse(cr, uid, ids[0], context=context)
        picking_ids = [picking.id for picking in
                       wave.picking_ids if picking.state == 'assigned']
        c = context.copy()
        c.update({'origin_wave': wave.id})
        return picking_obj.do_enter_transfer_details(
            cr, uid, picking_ids, context=c)

    @api.multi
    @api.onchange('partner')
    def onchange_partner(self):
        self.ensure_one()
        cond = [('state', 'not in', ('done', 'cancel'))]
        if self.partner:
            if self.partner.child_ids:
                ids = map(lambda x: x['id'], self.partner.child_ids)
                cond.extend(['|', ('partner_id', '=', self.partner.id),
                             ('partner_id', 'child_of', ids)])
            else:
                cond.extend([('partner_id', '=', self.partner.id)])
        return {'domain': {'picking_ids': cond}}


class StockMove(models.Model):
    _inherit = 'stock.move'

    wave = fields.Many2one('stock.picking.wave', related='picking_id.wave_id',
                           string='Picking Wave', store=True)
