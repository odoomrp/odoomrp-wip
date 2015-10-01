# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _
import openerp.addons.decimal_precision as dp


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'

    def lines_qty(self):
        return sum(self.quants_lines.mapped('qty'))

    @api.one
    @api.constrains('quants_lines')
    def check_qty(self):
        if self.quants_lines:
            total_qty = self.lines_qty()
            move = self.env['stock.move'].browse(self.env.context['active_id'])
            if total_qty > move.product_uom_qty:
                raise exceptions.Warning(
                    _('Error'), _('Quantity is higher than the needed one'))

    @api.depends('quants_lines')
    def get_move_qty(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        self.move_qty = move.product_uom_qty - self.lines_qty()

    name = fields.Char(string='Name')
    move_qty = fields.Float(string="Remaining qty", compute="get_move_qty")
    quants_lines = fields.One2many('assign.manual.quants.lines',
                                   'assign_wizard', string='Quants')

    @api.multi
    def assign_quants(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        move.picking_id.mapped('pack_operation_ids').unlink()
        quants = []
        for quant_id in move.reserved_quant_ids.ids:
            move.write({'reserved_quant_ids': [[3, quant_id]]})
        for line in self.quants_lines:
            if line.selected:
                quants.append([line.quant, line.qty])
        self.pool['stock.quant'].quants_reserve(
            self.env.cr, self.env.uid, quants, move, context=self.env.context)
        return {}

    @api.model
    def default_get(self, var_fields):
        res = super(AssignManualQuants, self).default_get(var_fields)
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        available_quants_ids = self.env['stock.quant'].search(
            ['|', ('location_id', '=', move.location_id.id),
             ('location_id', 'in', move.location_id.child_ids.ids),
             ('product_id', '=', move.product_id.id),
             ('qty', '>', 0),
             ('reservation_id', '=', False)])
        available_quants = [{
            'quant': x.id,
            'location_id': x.location_id.id,
        } for x in available_quants_ids]
        available_quants.extend({
            'quant': x.id,
            'selected': True,
            'qty': x.qty,
            'location_id': x.location_id.id,
        } for x in move.reserved_quant_ids)
        return {'quants_lines': available_quants}


class AssignManualQuantsLines(models.TransientModel):
    _name = 'assign.manual.quants.lines'
    _rec_name = 'quant'

    @api.multi
    @api.onchange('selected')
    def onchange_selected(self):
        for record in self:
            if not record.selected:
                record.qty = False
            elif not record.qty:
                quant_qty = record.quant.qty
                remaining_qty = record.assign_wizard.move_qty
                record.qty = (quant_qty if quant_qty < remaining_qty else
                              remaining_qty)

    assign_wizard = fields.Many2one(
        comodel_name='assign.manual.quants', string='Move', required=True,
        ondelete='cascade')
    quant = fields.Many2one(
        comodel_name='stock.quant', string='Quant', required=True,
        ondelete='cascade')
    location_id = fields.Many2one(
        comodel_name='stock.location', string='Location',
        related='quant.location_id', readonly=True)
    qty = fields.Float(
        string='QTY', digits=dp.get_precision('Product Unit of Measure'))
    selected = fields.Boolean(string='Select')
