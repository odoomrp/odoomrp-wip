
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 02/10/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
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
            if self.state != 'process':
                self.state = 'process'

    name = fields.Char('Name', required=True)
    new_component = fields.Many2one('product.product', 'New Component',
                                    required=True)
    old_component = fields.Many2one('product.product', 'Old Component',
                                    required=True)
    create_new_version = fields.Boolean(
        string="Create new BoM version", help='Check this field if you want to'
        ' create a new version of the BOM before modifying the component')
    state = fields.Selection([('draft', 'Draft'), ('process', 'In Process'),
                              ('done', 'Done')], 'State', default='draft',
                             required=True)
    boms = fields.Many2many(
        comodel_name='mrp.bom',
        relation='rel_mrp_bom_change', column1='bom_change_id',
        column2='bom_id', string='BoMs', copy=False, store=True,
        compute='_calc_boms')
    date = fields.Date('Change Date', readonly=True)
    user = fields.Many2one('res.users', 'Changed By', readonly=True)
    reason = fields.Char('Reason')

    @api.one
    def do_component_change(self):
        if not self.old_component or not self.new_component:
            raise exceptions.Warning(_("Not Components selected!"))
        if not self.boms:
            raise exceptions.Warning(_("There isn't any BoM for selected "
                                       "component"))
        for bom in self.boms:
            bom_lines = bom.bom_line_ids.filtered(
                lambda x: x.product_id.id == self.old_component.id)
            if bom_lines:
                if self.create_new_version:
                    new_bom = bom._copy_bom()
                    bom._update_bom_state_after_copy()
                    new_bom.button_activate()
                    self.boms = [(3, bom.id)]
                    self.boms = [(4, new_bom.id)]
                    bom_lines = new_bom.bom_line_ids.filtered(
                        lambda x: x.product_id.id == self.old_component.id)
                bom_lines.write({'product_id': self.new_component.id})
        self.write({'state': 'done', 'date': dt.now(), 'user': self.env.uid})

    @api.one
    def do_revert(self):
        data = self.copy()
        data.write({'name': _('Revert - ') + self.name,
                    'state': 'process',
                    'old_component': self.new_component.id,
                    'new_component': self.old_component.id,
                    'user': None, 'date': None})
        return True

    @api.one
    def clear_list(self):
        self.boms = [(6, 0, [])]
