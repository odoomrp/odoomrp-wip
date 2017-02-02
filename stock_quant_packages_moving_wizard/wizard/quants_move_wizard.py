# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockQuantsMoveWizard(models.TransientModel):
    _name = 'stock.quants.move'

    # TODO port v9: rename this field to remove 'pack_', which is confusing
    pack_move_items = fields.One2many(
        comodel_name='stock.quants.move_items', inverse_name='move_id',
        string='Quants')
    dest_loc = fields.Many2one(
        comodel_name='stock.location', string='Destination Location',
        required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(StockQuantsMoveWizard, self).default_get(fields_list)
        quants_ids = self.env.context.get('active_ids', [])
        if not quants_ids:
            return res
        quant_obj = self.env['stock.quant']
        quants = quant_obj.browse(quants_ids)
        items = []
        for quant in quants.filtered(lambda q: not q.package_id):
            items.append({'quant': quant.id})
        res.update(pack_move_items=items)
        return res

    @api.multi
    def do_transfer(self):
        self.ensure_one()
        quant_ids = []
        for item in self.pack_move_items:
            quant_ids.append(item.quant.id)
            if item.quant.location_id != self.dest_loc:
                item.quant.move_to(self.dest_loc)
        action = self.env['ir.actions.act_window'].for_xml_id(
            'stock', 'quantsact')
        action.update({
            'domain': [('id', 'in', quant_ids)],
            'context': {},
            })
        return action


class StockQuantsMoveItems(models.TransientModel):
    _name = 'stock.quants.move_items'
    _description = 'Picking wizard items'

    move_id = fields.Many2one(
        comodel_name='stock.quants.move', string='Quant move')
    quant = fields.Many2one(
        comodel_name='stock.quant', string='Quant', required=True,
        domain=[('package_id', '=', False)])
    source_loc = fields.Many2one(
        string='Current Location', related='quant.location_id', readonly=True)
