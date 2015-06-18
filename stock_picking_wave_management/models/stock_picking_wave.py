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

    @api.multi
    def confirm_picking(self):
        picking_obj = self.env['stock.picking']
        for wave in self:
            pickings = picking_obj.search([('wave_id', '=', wave.id),
                                           ('state', '=', 'draft')])
            pickings.action_assign()
            wave.state = 'in_progress'
        return True

    @api.one
    def button_check_availability(self):
        pickings = self.picking_ids.filtered(lambda x: x.state == 'confirmed')
        pickings.action_assign()

    # The old API is used because the father is updated method context
    def action_transfer(self, cr, uid, ids, context=None):
        picking_obj = self.pool['stock.picking']
        wave = self.browse(cr, uid, ids[0], context=context)
        pickings = wave.picking_ids.filtered(lambda x: x.state == 'assigned')
        c = context.copy()
        c.update({'origin_wave': wave.id})
        return picking_obj.do_enter_transfer_details(
            cr, uid, pickings.ids, context=c)

    @api.multi
    def _get_pickings_domain(self):
        self.ensure_one()
        cond = [('wave_id', '=', False),
                ('state', 'not in', ['done', 'cancel'])]
        if self.partner.child_ids:
            cond.extend(['|', ('partner_id', '=', self.partner.id),
                         ('partner_id', 'in',
                          self.partner.child_ids.ids)])
        elif self.partner:
            cond.extend([('partner_id', '=', self.partner.id)])
        return cond

    @api.multi
    @api.onchange('partner')
    def onchange_partner(self):
        self.ensure_one()
        cond = self._get_pickings_domain()
        return {'domain': {'picking_ids': cond}}
