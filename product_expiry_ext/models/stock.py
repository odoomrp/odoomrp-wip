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


class StockProductioLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.one
    @api.constrains('removal_date', 'alert_date', 'life_date', 'use_date')
    def _check_dates(self):
        dates = filter(lambda x: x, [self.alert_date, self.removal_date,
                                     self.use_date, self.life_date])
        sort_dates = list(dates)
        sort_dates.sort()
        if dates != sort_dates:
            raise exceptions.Warning(
                _('Dates must be: Alert Date < Removal Date < Best Before '
                  'Date < Expiry Date'))

    @api.one
    @api.depends('removal_date', 'alert_date', 'life_date', 'use_date')
    def _get_product_state(self):
        now = fields.Datetime.now()
        self.expiry_state = 'normal'
        if self.life_date and self.life_date < now:
            self.expiry_state = 'expired'
        elif (self.alert_date and self.removal_date and
                self.removal_date >= now > self.alert_date):
            self.expiry_state = 'alert'
        elif (self.removal_date and self.use_date and
                self.use_date >= now > self.removal_date):
            self.expiry_state = 'to_remove'
        elif (self.use_date and self.life_date and
                self.life_date >= now > self.use_date):
            self.expiry_state = 'best_before'

    expiry_state = fields.Selection(
        compute=_get_product_state,
        selection=[('expired', 'Expired'),
                   ('alert', 'In alert'),
                   ('normal', 'Normal'),
                   ('to_remove', 'To remove'),
                   ('best_before', 'After the best before')],
        string='Expiry state')


class StockQuant(models.Model):

    _inherit = "stock.quant"

    expiry_state = fields.Selection(string="Expiry State",
                                    related="lot_id.expiry_state")
