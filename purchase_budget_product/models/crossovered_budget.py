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

from openerp import models, api


class CrossoveredBudget(models.Model):

    _inherit = 'crossovered.budget'

    @api.multi
    def load_purchases_on_budget(self):
        self.ensure_one()
        load_wiz_obj = self.env['load.purchases.on.budget']
        load_wiz_view = self.env.ref('purchase_budget_product.load_purchases_'
                                     'on_budget_budget_form_view')
        load_wiz_vals = {'budget_id': self.id}
        wiz_id = load_wiz_obj.create(load_wiz_vals)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'load.purchases.on.budget',
            'views': [(load_wiz_view.id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wiz_id.id
            }
