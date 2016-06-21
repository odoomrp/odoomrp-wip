# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ProcurementSaleForecast(models.Model):
    _inherit = 'procurement.sale.forecast'

    @api.multi
    def create_procurements(self):
        result = super(ProcurementSaleForecast, self).create_procurements()
        for record in self:
            for line in record.forecast_lines.filtered(
                    lambda x: x.procurement_id and not
                    x.procurement_id.origin):
                origin = ('MPS: ' + record.name + ' (' + record.date_from +
                          '.' + record.date_to + ') ' +
                          record.warehouse_id.name)
                line.procurement_id.write({'origin': origin,
                                           'level': 1000})
        return result
