# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class MakeProcurement(models.TransientModel):
    _inherit = 'make.procurement'

    @api.multi
    def make_procurement(self):
        result = super(MakeProcurement, self).make_procurement()
        forecast_line_obj = self.env['procurement.sale.forecast.line']
        procurement_obj = self.env['procurement.order']
        context = self.env.context
        if context.get('active_model') == 'procurement.sale.forecast.line':
            line = forecast_line_obj.browse(context['active_id'])
            procurement = procurement_obj.browse(result['res_id'])
            origin = ('MPS: ' + line.forecast_id.name + ' (' +
                      line.forecast_id.date_from + '.' +
                      line.forecast_id.date_to + ') ' +
                      line.forecast_id.warehouse_id.name)
            procurement.write({'origin': origin,
                               'level': 1000})
        return result
