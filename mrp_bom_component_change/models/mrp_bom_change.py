
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


class MrpBomChange(models.Model):
    _name = 'mrp.bom.change'
    _descrition = 'Mrp BOM Component Change'

    name = fields.Char('Name', required=True)
    component = fields.Many2one('product.product', 'Selected Component')
    comp2mod = fields.Many2one('product.product', 'Component to Modify')
    state = fields.Selection([('draft', 'Draft'), ('process', 'In Process'),
                              ('done', 'Done')], 'State', default='draft',
                             required=True)
    boms = fields.Many2many('mrp.bom', 'mrp_bom_change_rel', 'bom_change',
                            'bom_id')

    @api.one
    @api.onchange('component')
    def onchange_operation(self):
        bom_obj = self.env['mrp.bom']
        bom_lst = []
        for bom in bom_obj.search([]):
            for bom_line in bom.bom_line_ids:
                if bom_line.product_id.id == self.component.id:
                    bom_lst.append(bom.id)
                    break
        self.boms = bom_lst
        self.state = 'process'

    @api.one
    def do_component_change(self):
        if not self.component or not self.comp2mod:
            raise exceptions.Warning(_("Not Components selected!"))
        if not self.boms:
            raise exceptions.Warning(_("There is no BOM list for current "
                                       "selected component!"))
        for bom in self.boms:
            for bom_line in bom.bom_line_ids:
                if bom_line.product_id.id == self.component.id:
                    bom_line.product_id = self.comp2mod.id
        self.state = 'done'

    @api.one
    def do_revert(self):
        data = self.copy()
        data.write({'name': _('Revert - ') + self.name,
                    'state': 'process',
                    'component': self.comp2mod.id,
                    'comp2mod': self.component.id})
        return True
