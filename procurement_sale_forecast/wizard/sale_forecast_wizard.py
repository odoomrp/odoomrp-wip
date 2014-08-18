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

from openerp.osv import orm, fields
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime


class SaleForecastWizard(orm.TransientModel):
    _name = 'product.sale.forecast.wizard'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'product_id': fields.many2one('product.product', 'Product'),
        'ref_date': fields.date('Reference date', required=True),
        'period': fields.integer('Period (month number)', required=True),
        'start_date': fields.date('Forecasted start date', required=True),
    }

    _rec_name = 'start_date'

    def action_generate_sale_forecast(self, cr, uid, ids, context=None):
        for id in ids:
            data = self.browse(cr, uid, id, context=context)
            proc_obj = self.pool['procurement.order']
            sale_proc_obj = self.pool['sale.forecast.procurement']
            domain = [['state','=','done']]
            values = {}
            if data.partner_id:
                domain.append(['partner_id', '=', data.partner_id.id])
            if data.product_id:
                domain.append(['product_id', '=', data.product_id.id])
            qty = {}
            for num in range(1,data.period+1):
                start = datetime.strptime(data.ref_date, '%Y-%m-%d') + relativedelta(months = num-1)
                end = datetime.strptime(data.ref_date, '%Y-%m-%d') + relativedelta(months = num)
                date = datetime.strptime(data.start_date, '%Y-%m-%d') + relativedelta(months = num-1)
                domain.append(['date_planned', '>', str(start)])
                domain.append(['date_planned', '<=', str(end)])
                values['date'] = str(date)
                proc_ids = proc_obj.search(cr, uid, domain, context=context)
                for proc in proc_obj.browse(cr, uid, proc_ids, context=context):
                    if proc.partner_id.id in qty:
                        if proc.product_id.id in qty[proc.partner_id.id]:
                            qty[proc.partner_id.id][proc.product_id.id] += proc.product_qty
                        else:
                            qty[proc.partner_id.id][proc.product_id.id] = proc.product_qty
                    else:
                        qty[proc.partner_id.id] = {}
                        qty[proc.partner_id.id][proc.product_id.id] = proc.product_qty
                for partner_id in qty.keys():
                    for product_id in qty[partner_id].keys():
                        values.update(
                            {'partner_id': partner_id,
                             'product_id': product_id,
                             'qty': qty[partner_id][product_id]})
                        sale_proc_obj.create(cr, uid, values, context=context)
        return True
