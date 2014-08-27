
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 26/08/2014
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

from openerp import fields, models, api, exceptions
from openerp.tools.translate import _


class StockPicking(models.Model):
    _description = 'stock picking Inheritance'
    _inherit = 'stock.picking'

    crm_name = fields.Many2one('crm.claim', string='CRM Claim', select=True)
    suppliref = fields.Char(string='Supplier ref', select=True,
                            help='Supplier reference number')

    @api.multi
    def action_stock_return_picking(self):
        if not self.crm_name:
            raise exceptions.except_orm(_('Error'),
                                        _("Selected Picking has no claim order"
                                          " assigned"))
        else:
            context = self.env.context.copy()
            context['active_id'] = self.id
            context['active_ids'] = self.ids
            context['active_model'] = 'stock.picking'
            self.env.context = context
            return {'name': _('Return Shipment'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.return.picking',
                    'target': 'new',
                    'context': self.env.context,
                    }
