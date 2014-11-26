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

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    property_mandatory_carrier = fields.Many2one(
        comodel_name='delivery.carrier', string='Mandatory delivery method',
        related='partner_id.property_mandatory_carrier')

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(SaleOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)
        res['value'].update({'carrier_id': False})
        partner_obj = self.pool['res.partner']
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        if partner.property_mandatory_carrier:
            res['value'].update(
                {'carrier_id': partner.property_mandatory_carrier.id})
        if partner.banned_carrier_ids:
            res.update({'domain':
                        {'carrier_id':
                         [('id', 'not in', partner.banned_carrier_ids.ids)]}})
        else:
            res.update({'domain': {'carrier_id': []}})
        return res
