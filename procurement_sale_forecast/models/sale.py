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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class ProcurementSaleForecast(models.Model):
    _name = 'procurement.sale.forecast'

    @api.one
    @api.depends('forecast_lines.procurement_id')
    def _get_procurement_count(self):
        procurement_lst = []
        for line in self.forecast_lines:
            if line.procurement_id:
                procurement_lst.append(line.procurement_id.id)
        self.procurement_count = len(procurement_lst)

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    forecast_lines = fields.One2many('procurement.sale.forecast.line',
                                     'forecast_id', string="Forecast Lines")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    procurement_count = fields.Integer(string="Procurement Count",
                                       compute=_get_procurement_count)

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from >= self.date_to:
            raise exceptions.Warning(_('Error! Date to must be lower '
                                       'than date from.'))

    @api.multi
    def create_procurements(self):
        procurement_obj = self.env['procurement.order']
        procure_lst = []
        for record in self:
            for product_line in record.forecast_lines:
                if product_line.product_id and not product_line.procurement_id:
                    procure_id = procurement_obj.create({
                        'name': (
                            'MPS: ' + record.name + ' (' + record.date_from +
                            '.' + record.date_to + ') ' +
                            record.warehouse_id.name),
                        'date_planned': product_line.date,
                        'product_id': product_line.product_id.id,
                        'product_qty': product_line.qty,
                        'product_uom': product_line.product_id.uom_id.id,
                        'location_id': record.warehouse_id.lot_stock_id.id,
                        'company_id': record.warehouse_id.company_id.id,
                        'warehouse_id': record.warehouse_id.id,
                    })
                    procure_id.signal_workflow('button_confirm')
                    procure_lst.append(procure_id.id)
                    product_line.procurement_id = procure_id.id
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_ids': procure_lst,
            'domain': [('id', 'in', procure_lst)],
            'type': 'ir.actions.act_window',
            }

    @api.multi
    def show_all_forecast_procurements(self):
        procurement_list = []
        for record in self:
            for line in record.forecast_lines:
                if line.procurement_id:
                    procurement_list.append(line.procurement_id.id)
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_ids': procurement_list,
            'domain': [('id', 'in', procurement_list)],
            'type': 'ir.actions.act_window',
            }


class ProcurementSaleForecastLine(models.Model):

    _name = 'procurement.sale.forecast.line'

    @api.one
    @api.depends('unit_price', 'qty')
    def _get_subtotal(self):
        self.subtotal = self.unit_price * self.qty

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.unit_price = self.product_id.list_price

    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one('product.category',
                                          string='Product Category')
    qty = fields.Float('Quantity', default=1,
                       digits_compute=dp.get_precision('Product Unit of'
                                                       ' Measure'))
    unit_price = fields.Float('Unit Price',
                              digits_compute=dp.get_precision('Product Price'))
    subtotal = fields.Float('Subtotal', compute=_get_subtotal, store=True,
                            digits_compute=dp.get_precision('Product Price'))
    partner_id = fields.Many2one("res.partner", string="Partner")
    date_from = fields.Date(string="Date from", store=True,
                            related="forecast_id.date_from")
    date_to = fields.Date(string="Date to", related="forecast_id.date_to",
                          store=True)
    forecast_id = fields.Many2one('procurement.sale.forecast',
                                  string='Forecast')
    procurement_id = fields.Many2one('procurement.order', string="Procurement")
    date = fields.Date("Date", required=True)

    _order = 'date asc'

    @api.multi
    def request_procurement(self):
        self.ensure_one()
        value_dict = {'product_id': self.product_id.id,
                      'uom_id': self.product_id.uom_id.id,
                      'date_planned': self.date,
                      'qty': self.qty,
                      'warehouse_id': self.forecast_id.warehouse_id.id
                      }
        res_id = self.env['make.procurement'].create(value_dict)
        return {'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'make.procurement',
                'res_id': res_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
