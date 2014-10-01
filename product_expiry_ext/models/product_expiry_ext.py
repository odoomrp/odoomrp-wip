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
from openerp import _


class StockProductioLot(orm.Model):
    _inherit = 'stock.production.lot'

    def _get_dates(self, cr, uid, lot, context=None):
            removal_date = lot.removal_date and \
                datetime.strptime(lot.removal_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT) or False
            alert_date = lot.alert_date and \
                datetime.strptime(lot.alert_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT) or False
            life_date = lot.life_date and \
                datetime.strptime(lot.life_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT) or False
            use_date = lot.life_date and \
                datetime.strptime(lot.use_date,
                                  DEFAULT_SERVER_DATETIME_FORMAT) or False
            return alert_date, removal_date, use_date, life_date

    def _check_dates(self, cr, uid, ids, context=None):
        lots = self.browse(cr, uid, ids, context=context)
        for lot in lots:
            dates = filter(lambda x: x, [lot.alert_date, lot.removal_date,
                                         lot.use_date, lot.life_date])
            sort_dates = list(dates)
            sort_dates.sort()
            if dates != sort_dates:
                return False
        return True

    def _get_product_state(self, cr, uid, ids, field_name, args,
                           context=None):
        res = {}
        today = datetime.now()
        for lot in self.browse(cr, uid, ids, context=context):
            alert_date, removal_date, use_date, life_date = self._get_dates(
                cr, uid, lot, context=context)
            res[lot.id] = 'normal'
            if life_date and life_date < today:
                res[lot.id] = 'expired'
                continue
            if alert_date and removal_date and today > alert_date and \
                    today <= removal_date:
                res[lot.id] = 'alert'
                continue
            if removal_date and use_date and today > removal_date and \
                    today <= use_date:
                res[lot.id] = 'to_remove'
                continue
            if use_date and life_date and today > use_date and \
                    today <= life_date:
                res[lot.id] = 'best_before'
                continue
        return res

    _columns = {
        'expiry_state': fields.function(
            _get_product_state, type='selection',
            selection=[('expired', 'Expired'),
                       ('alert', 'In alert'),
                       ('normal', 'Normal'),
                       ('to_remove', 'To remove'),
                       ('best_before', 'After the best before')],
            string='Expiry state'),
    }

    _constraints = [(_check_dates, _('Dates must be: Alert Date < Removal Date'
                    '< Best Before Date < Expiry Date'),
                     ['alert_date', 'removal_date', 'use_date', 'life_date'])]
