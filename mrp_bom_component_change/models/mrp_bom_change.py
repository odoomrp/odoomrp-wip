# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from datetime import datetime as dt


class MrpBomChange(models.Model):
    _name = 'mrp.bom.change'
    _description = 'Mrp BoM Component Change'

    @api.one
    @api.depends('old_component')
    def _calc_boms(self):
        self.boms = [(6, 0, [])]
        if self.old_component:
            for bom in self.env['mrp.bom'].search([]):
                bom_lines = bom.bom_line_ids.filtered(
                    lambda x: x.product_id.id == self.old_component.id)
                if bom_lines:
                    self.boms = [(4, bom.id)]

    name = fields.Char('Name', required=True)
    new_component = fields.Many2one('product.product', 'New Component',
                                    required=True)
    old_component = fields.Many2one('product.product', 'Old Component',
                                    required=True)
    create_new_version = fields.Boolean(
        string="Create new BoM version", help='Check this field if you want to'
        ' create a new version of the BOM before modifying the component')
    boms = fields.Many2many(
        comodel_name='mrp.bom',
        relation='rel_mrp_bom_change', column1='bom_change_id',
        column2='bom_id', string='BoMs', copy=False, store=True, readonly=True,
        compute='_calc_boms')
    date = fields.Date('Change Date', readonly=True)
    user = fields.Many2one('res.users', 'Changed By', readonly=True)
    reason = fields.Char('Reason')

    @api.multi
    def do_component_change(self):
        self.ensure_one()
        if not self.old_component or not self.new_component:
            raise exceptions.Warning(_("Not Components selected!"))
        if not self.boms:
            raise exceptions.Warning(_("There isn't any BoM for selected "
                                       "component"))
        for bom in self.boms:
            bom_lines = bom.bom_line_ids.filtered(
                lambda x: x.product_id.id == self.old_component.id)
            if self.create_new_version:
                new_bom = bom._copy_bom()
                bom.button_historical()
                new_bom.button_activate()
                self.boms = [(3, bom.id)]
                self.boms = [(4, new_bom.id)]
                bom_lines = new_bom.bom_line_ids.filtered(
                    lambda x: x.product_id.id == self.old_component.id)
            bom_lines.write({'product_id': self.new_component.id})
        self.write({'date': dt.now(), 'user': self.env.uid})
        return {'name': _('Bill of Material'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'mrp.bom',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.boms.mapped('id'))]
                }
