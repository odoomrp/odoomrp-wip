
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

    name = fields.Char('Name', required=True)
    new_component = fields.Many2one('product.product', 'New Component')
    old_component = fields.Many2one('product.product', 'Old Component')
    state = fields.Selection([('draft', 'Draft'), ('process', 'In Process'),
                              ('done', 'Done')], 'State', default='draft',
                             required=True)
    boms = fields.Many2many('mrp.bom', 'mrp_bom_change_rel', 'bom_change',
                            'bom_id')
    date = fields.Date('Change Date', readonly=True)
    user = fields.Many2one('res.users', 'Changed By', readonly=True)
    reason = fields.Char('Reason')

    @api.multi
    @api.onchange('old_component')
    def onchange_operation(self):
        if self.old_component:
            bom_obj = self.env['mrp.bom']
            bom_lst = []
            for bom in bom_obj.search([]):
                for bom_line in bom.bom_line_ids:
                    if bom_line.product_id.id == self.old_component.id:
                        bom_lst.append(bom.id)
                        break
            self.boms = bom_lst
            if self.state != 'process':
                self.state = 'process'
        return {'domain': {'boms': [('id', 'in', bom_lst)]}}

    @api.one
    def do_component_change(self):
        if not self.old_component or not self.new_component:
            raise exceptions.Warning(_("Not Components selected!"))
        if not self.boms:
            raise exceptions.Warning(_("There isn't any BoM for selected "
                                       "component"))
        for bom in self.boms:
            for bom_line in bom.bom_line_ids:
                if bom_line.product_id.id == self.old_component.id:
                    bom_line.product_id = self.new_component.id
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
        for bom_id in self.boms.ids:
            self.boms = [(5, bom_id)]
