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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, values):
        sale_obj = self.env['sale.order']
        picking = False
        if values.get('picking_id'):
            picking = self.env['stock.picking'].browse(values['picking_id'])
        group_id = values.get('group_id', False)
        for rec in self:
            res_picking = picking or rec.picking_id
            if not group_id and rec.group_id:
                group_id = rec.group_id.id
            orders = sale_obj.search([('procurement_group_id', '=', group_id)])
            if orders and res_picking:
                inv_type = orders[0].invoice_type_id.id
                res_picking.write({'invoice_type_id': inv_type})
        return super(StockMove, self).write(values)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool['res.partner']
        result = super(StockPicking, self).onchange_partner_id(cr, uid, ids,
                                                               partner_id,
                                                               context=context)
        if partner_id:
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            itype = partner.property_invoice_type
            if itype:
                result['value']['invoice_type_id'] = itype.id
        return result

    def action_invoice_create(self, cr, uid, ids, journal_id, group=False,
                              type='out_invoice', context=None):
        sale_journal_type = self.pool['sale_journal.invoice.type']
        grouped_type = sale_journal_type.search(cr, uid,
                                                [('invoicing_method', '=',
                                                  'grouped')],
                                                context=context)
        group_picking_lst = self.search(cr, uid,
                                        [('invoice_type_id', 'in',
                                          grouped_type), ('id', 'in', ids)],
                                        context=context)
        for pick_id in group_picking_lst:
            ids.remove(pick_id)
        result = []
        if group_picking_lst:
            result += super(StockPicking, self).action_invoice_create(
                cr, uid, group_picking_lst, journal_id, group=True, type=type,
                context=context)
        if ids:
            result += super(StockPicking, self).action_invoice_create(
                cr, uid, ids, journal_id, group=False, type=type,
                context=context)
        return result
