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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_mandatory_carrier = fields.Many2one(
        'delivery.carrier', string='Mandatory delivery method',
        company_dependent=True)
    banned_carrier_ids = fields.Many2many(
        comodel_name='delivery.carrier', relation='rel_partner_banned_carrier',
        column1='partner_id', column2='carrier_id',
        string='Banned delivery carrier')

    @api.constrains('property_mandatory_carrier', 'banned_carrier_ids')
    def mandatory_no_banned(self):
        if self.property_mandatory_carrier in self.banned_carrier_ids:
            raise exceptions.Warning(_('It is not possible to have the'
                                       ' mandatory carrier as banned one and'
                                       ' viceversa, please check carrier: %s')
                                     % self.property_mandatory_carrier.name)
