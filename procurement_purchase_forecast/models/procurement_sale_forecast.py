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


class ProcurementSaleForecast(models.Model):

    _inherit = 'procurement.sale.forecast'

    @api.multi
    def load_purchases_to_forecast(self):
        self.ensure_one()
        load_wiz_obj = self.env['purchase.forecast.load']
        load_wiz_view = self.env.ref('procurement_purchase_forecast.purchase_'
                                     'forecast_load_forecast_form_view')
        load_wiz_vals = {'forecast_id': self.id,
                         'date_from': self.date_from,
                         'date_to': self.date_to
                         }
        wiz_id = load_wiz_obj.create(load_wiz_vals)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.forecast.load',
            'views': [(load_wiz_view.id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wiz_id.id
            }
