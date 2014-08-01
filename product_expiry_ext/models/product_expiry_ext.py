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

from datetime import datetime
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockProductioLot(orm.Model):
    _inherit = 'stock.production.lot'

    def _get_product_state(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        today = datetime.today()
        for lot in self.browse(cr, uid, ids, context=context):
            if lot.removal_date:
                removal_date = lot.removal_date and \
                    datetime.strptime(lot.removal_date,
                                      DEFAULT_SERVER_DATETIME_FORMAT)
            if lot.alert_date:
                alert_date = lot.alert_date and \
                    datetime.strptime(lot.alert_date,
                                      DEFAULT_SERVER_DATETIME_FORMAT)
            if lot.life_date:
                life_date = lot.life_date and \
                    datetime.strptime(lot.life_date,
                                      DEFAULT_SERVER_DATETIME_FORMAT)
            res[lot.id] = 'normal'
            if life_date and life_date < today:
                res[lot.id] = 'expired'
            elif removal_date and alert_date:
                if removal_date > alert_date and removal_date <= today:
                    res[lot.id] = 'to_remove'
                elif today >= alert_date and alert_date > removal_date \
                    or alert_date < removal_date:
                    res[lot.id] = 'alert'
            elif alert_date:
                if alert_date <= today:
                    res[lot.id] = 'alert'
        return res

    _columns = {
        'expiry_state': fields.function(
            _get_product_state, type='selection',
            selection=[('expired', 'Expired'),
                       ('alert', 'In alert'),
                       ('normal', 'Normal'),
                       ('to_remove', 'To remove')],
            string='Product Expiry State'),
    }
