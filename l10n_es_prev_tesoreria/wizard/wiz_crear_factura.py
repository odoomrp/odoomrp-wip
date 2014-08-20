# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import orm, fields


class WizCrearFactura(orm.TransientModel):
    _name = 'wiz.crear.factura'
    _description = 'Asistente para crear las facturas'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Empresa', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Diario',
                                      domain=[('type', '=', 'purchase')],
                                      required=True),
        'description': fields.char('Descripción', size=64, required=True),
        'importe': fields.float('Importe',
                                digits_compute=dp.get_precision('Account')),
        'pago': fields.integer('Pago'),
        'type': fields.char('Tipo de Pago', size=1),
    }

    def default_get(self, cr, uid, fields_list, context=None):
        values = {}
        if context['active_model'] == "l10n.es.tesoreria.pagos.var.plan":
            obj = self.pool['l10n.es.tesoreria.pagos.var.plan']
            type = 'V'
        else:
            obj = self.pool['l10n.es.tesoreria.pagos.period.plan']
            type = 'P'
        for pago in obj.browse(cr, uid, context['active_ids'],
                               context=context):
            if pago.factura_id:
                raise orm.except_orm(
                    _('Error!'),
                    _('Este pago ya tiene una factura asignado!!'))
            values = {
                'partner_id': pago.partner_id.id,
                'journal_id': pago.diario.id,
                'description': pago.name,
                'importe': pago.importe,
                'pago': int(pago.id),
                'type': type,
            }
        return values

    def button_create_inv(self, cr, uid, ids, context=None):
        invoice_obj = self.pool['account.invoice']
        address_obj = self.pool['res.partner.address']
        for wiz in self.browse(cr, uid, ids, context=context):
            address = address_obj.search(cr, uid, [('partner_id', '=',
                                                    wiz.partner_id.id)])
            if address:
                values = {
                    'name': 'Prev: ' + wiz.description +
                    '/ Importe: ' + str(wiz.importe),
                    'reference': 'Prev: ' + wiz.description +
                    '/ Importe: ' + str(wiz.importe),
                    'partner_id': wiz.partner_id.id,
                    'journal_id': wiz.journal_id.id,
                    'address_invoice_id': address[0],
                    'type': 'in_invoice',
                    'account_id':
                        wiz.partner_id.property_account_receivable.id,
                }
                if wiz.partner_id.property_payment_term:
                    values.update({'payment_term':
                                   wiz.partner_id.property_payment_term.id})
                if wiz.partner_id.payment_type_customer:
                    values.update({'payment_type':
                                   wiz.partner_id.payment_type_customer.id})
                if wiz.partner_id.property_account_position:
                    values.update(
                        {'fiscal_position':
                         wiz.partner_id.property_account_position.id})
            else:
                raise orm.except_orm(_('Error!'),
                                     _('Address not found for Partner: '),
                                     wiz.partner_id.name)
            invoice_id = invoice_obj.create(cr, uid, values)
            if wiz.type == 'V':
                obj = self.pool['l10n.es.tesoreria.pagos.var.plan']
            else:
                obj = self.pool['l10n.es.tesoreria.pagos.period.plan']
            obj.write(cr, uid, wiz.pago, {'factura_id': invoice_id,
                                          'diario': wiz.journal_id.id,
                                          'pagado': 1})
        return {'type': 'ir.actions.act_window_close'}
