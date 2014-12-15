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


class MakeProcurement(models.TransientModel):

    _inherit = 'make.procurement'

    @api.multi
    def make_procurement(self):
        result = super(MakeProcurement, self).make_procurement()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        context = self.env.context
        if context.get('active_model') == 'procurement.sale.forecast.line':
            forecast_line_id = context['active_id']
            procurement_id = result['res_id']
            forecast_line = forecast_line_obj.browse(forecast_line_id)
            forecast_line.procurement_id = procurement_id
        return result
