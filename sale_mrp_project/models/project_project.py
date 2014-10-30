# -*- encoding: utf-8 -*-
##############################################################################
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

from openerp import models, fields, api


class ProjectProject(models.Model):

    _inherit = 'project.project'

    @api.one
    def _project_shortcut_count(self):
        purchase_obj = self.env['purchase.order']
        sale_obj = self.env['sale.order']
        production_obj = self.env['mrp.production']
        procurement_obj = self.env['procurement.order']
        purchases = purchase_obj.search([('general_project_id', '=', self.id)])
        sales = sale_obj.search([('general_project_id', '=', self.id)])
        productions = production_obj.search([('project_id', '=', self.id)])
        procurements = procurement_obj.search([('general_project_id', '=',
                                                self.id)])
        self.purchase_count = len(purchases)
        self.sale_count = len(sales)
        self.production_count = len(productions)
        self.procurement_count = len(procurements)
        return True

    purchase_count = fields.Integer(string='Purchase Count',
                                    compute=_project_shortcut_count)
    sale_count = fields.Integer(string='Sale Count',
                                compute=_project_shortcut_count)
    production_count = fields.Integer(string='Manufacturing Count',
                                      compute=_project_shortcut_count)
    procurement_count = fields.Integer(string='Procurement Count',
                                       compute=_project_shortcut_count)
