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
from openerp.osv import orm, fields
import pyExcelerator as xl
import StringIO
import base64


class L10nEsTesoreriaFacturas(orm.Model):
    _inherit = 'l10n.es.tesoreria.facturas'

    _columns = {
        'inv_type': fields.related('factura_id', 'type', type="selection",
                                   selection=[('out_invoice',
                                              'Customer Invoice'),
                                              ('in_invoice',
                                              'Supplier Invoice'),
                                              ('out_refund',
                                               'Customer Refund'),
                                              ('in_refund', 'Supplier Refund'),
                                              ], string="Tipo"),
        'payment_term': fields.many2one('account.payment.term',
                                        'Plazo de Pago'),
    }


class L10nEsTesoreria(orm.Model):
    _inherit = 'l10n.es.tesoreria'

    def _calcular_saldo(self, cr, uid, ids, name, args, context=None):
        res = {}
        saldo = 0
        for teso in self.browse(cr, uid, ids, context=context):
            for fact_emit in teso.facturas_emit:
                saldo += fact_emit.total
            for fact_rec in teso.facturas_rec:
                saldo -= fact_rec.total
            for pagoP in teso.pagos_period:
                saldo -= pagoP.importe
            for pagoV in teso.pagos_var:
                saldo -= pagoV.importe
            for pagoR in teso.pagos_rece:
                saldo += pagoR.importe
            for pagoC in teso.pagos_cash:
                saldo += pagoC.importe
            saldo += teso.saldo_inicial
            res[teso.id] = saldo
        return res

    _columns = {'pagos_rece': fields.one2many('l10n.es.tesoreria.pagos.rece',
                                              'tesoreria_id', 'Cobros Unicos'),
                'pagos_cash': fields.one2many('l10n.es.tesoreria.pagos.cash',
                                              'tesoreria_id',
                                              'Cash-flow Financiero'),
                'saldo_final': fields.function(
                    _calcular_saldo, method=True,
                    digits_compute=dp.get_precision('Account'),
                    string='Saldo Final'),
                }

    def button_saldo(self, cr, uid, ids, context=None):
        saldo = 0
        saldos_obj = self.pool['l10n.es.tesoreria.saldos']
        for teso in self.browse(cr, uid, ids, context=context):
            for saldo in teso.desglose_saldo:
                saldos_obj.unlink(cr, uid, saldo.id, context=context)
            for fact_emit in teso.facturas_emit:
                abs_emit_total = fact_emit.total
                if abs_emit_total < 0:
                    abs_emit_total = - abs_emit_total
#                if fact_emit.tipo_pago:
#                    name = fact_emit.tipo_pago.name
#                else:
                name = 'Undefined'
                if fact_emit.inv_type == 'out_invoice':
                    saldo_id = saldos_obj.search(
                        cr, uid, [('name', '=', name),
                                  ('tesoreria_id', '=', teso.id),
                                  ('type', '=', 'in')], context=context)
                    if saldo_id:
                        saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                                  context=context)
                        saldos_obj.write(cr, uid, saldo.id,
                                         {'saldo': saldo.saldo +
                                          abs_emit_total}, context=context)
                    else:
                        saldos_obj.create(cr, uid, {'name': name,
                                                    'saldo': abs_emit_total,
                                                    'tesoreria_id': teso.id,
                                                    'type': 'in'},
                                          context=context)
                if fact_emit.inv_type == 'out_refund':
                    saldo_id = saldos_obj.search(
                        cr, uid, [('name', '=', name),
                                  ('tesoreria_id', '=', teso.id),
                                  ('type', '=', 'out')], context=context)
                    if saldo_id:
                        saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                                  context=context)
                        saldos_obj.write(cr, uid, saldo.id,
                                         {'saldo': saldo.saldo +
                                          abs_emit_total}, context=context)
                    else:
                        saldos_obj.create(cr, uid, {'name': name,
                                                    'saldo': abs_emit_total,
                                                    'tesoreria_id': teso.id,
                                                    'type': 'out'},
                                          context=context)
            for fact_rec in teso.facturas_rec:
                abs_rec_total = fact_rec.total
                if abs_rec_total < 0:
                    abs_rec_total = - abs_rec_total
#                if fact_emit.tipo_pago:
#                    name = fact_emit.tipo_pago.name
#                else:
                name = 'Undefined'
                if fact_rec.inv_type == 'in_invoice':
                    saldo_id = saldos_obj.search(
                        cr, uid, [('name', '=', name),
                                  ('tesoreria_id', '=', teso.id),
                                  ('type', '=', 'out')], context=context)
                    if saldo_id:
                        saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                                  context=context)
                        saldos_obj.write(cr, uid, saldo.id,
                                         {'saldo': saldo.saldo +
                                          abs_rec_total}, context=context)
                    else:
                        saldos_obj.create(cr, uid,
                                          {'name': name,
                                           'saldo': abs_rec_total,
                                           'tesoreria_id': teso.id,
                                           'type': 'out'}, context=context)
                if fact_rec.inv_type == 'in_refund':
                    saldo_id = saldos_obj.search(
                        cr, uid, [('name', '=', name),
                                  ('tesoreria_id', '=', teso.id),
                                  ('type', '=', 'in')], context=context)
                    if saldo_id:
                        saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                                  context=context)
                        saldos_obj.write(cr, uid, saldo.id,
                                         {'saldo': saldo.saldo +
                                          abs_rec_total}, context=context)
                    else:
                        saldos_obj.create(cr, uid, {'name': name,
                                                    'saldo': abs_rec_total,
                                                    'tesoreria_id': teso.id,
                                                    'type': 'in'},
                                          context=context)
            for pagoV in teso.pagos_var:
                abs_pagov_importe = pagoV.importe
                if abs_pagov_importe < 0:
                    abs_pagov_importe = - abs_pagov_importe
#                if pagoV.payment_type:
#                    name = pagoV.payment_type.name
#                else:
                name = 'Undefined'
                saldo_id = saldos_obj.search(cr, uid,
                                             [('name', '=', name),
                                              ('tesoreria_id', '=', teso.id),
                                              ('type', '=', 'out')],
                                             context=context)
                if saldo_id:
                    saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                              context=context)
                    saldos_obj.write(cr, uid, saldo.id,
                                     {'saldo': saldo.saldo +
                                      abs_pagov_importe}, context=context)
                else:
                    saldos_obj.create(cr, uid, {'name': name,
                                                'saldo': abs_pagov_importe,
                                                'tesoreria_id': teso.id,
                                                'type': 'out'},
                                      context=context)
            for pagoP in teso.pagos_period:
                abs_pagop_importe = pagoP.importe
                if abs_pagop_importe < 0:
                    abs_pagop_importe = - abs_pagop_importe
#                if pagoP.payment_type:
#                    name = pagoP.payment_type.name
#                else:
                name = 'Undefined'
                saldo_id = saldos_obj.search(cr, uid,
                                             [('name', '=', name),
                                              ('tesoreria_id', '=', teso.id),
                                              ('type', '=', 'out')],
                                             context=context)
                if saldo_id:
                    saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                              context=context)
                    saldos_obj.write(cr, uid, saldo.id, {'saldo': saldo.saldo +
                                                         abs_pagop_importe},
                                     context=context)
                else:
                    saldos_obj.create(cr, uid, {'name': name,
                                                'saldo': abs_pagop_importe,
                                                'tesoreria_id': teso.id,
                                                'type': 'out'},
                                      context=context)
            for pagoR in teso.pagos_rece:
                abs_pagor_importe = pagoR.importe
                if abs_pagor_importe < 0:
                    abs_pagor_importe = - abs_pagor_importe
#                if pagoR.payment_type:
#                    name = pagoR.payment_type.name
#                else:
                name = 'Undefined'
                saldo_id = saldos_obj.search(cr, uid,
                                             [('name', '=', name),
                                              ('tesoreria_id', '=', teso.id),
                                              ('type', '=', 'in')],
                                             context=context)
                if saldo_id:
                    saldo = saldos_obj.browse(cr, uid, saldo_id[0],
                                              context=context)
                    saldos_obj.write(cr, uid, saldo.id, {'saldo': saldo.saldo +
                                                         abs_pagor_importe},
                                     context=context)
                else:
                    saldos_obj.create(cr, uid, {'name': name,
                                                'saldo': abs_pagor_importe,
                                                'tesoreria_id': teso.id,
                                                'type': 'in'}, context=context)
            for pagoC in teso.pagos_cash:
                abs_pagoc_importe = pagoC.importe
                if abs_pagoc_importe < 0:
                    abs_pagoc_importe = - abs_pagoc_importe
#                if pagoC.payment_type:
#                    name = pagoC.payment_type.name
#                else:
                name = 'Undefined'
                saldo_id = saldos_obj.search(cr, uid,
                                             [('name', '=', name),
                                              ('tesoreria_id', '=', teso.id),
                                              ('type', '=', pagoC.type)],
                                             context=context)
                if saldo_id:
                    saldo = saldos_obj.browse(cr, uid, saldo_id[0])
                    saldos_obj.write(cr, uid, saldo.id, {'saldo': saldo.saldo +
                                                         abs_pagoc_importe},
                                     context=context)
                else:
                    saldos_obj.create(cr, uid, {'name': name,
                                                'saldo': abs_pagoc_importe,
                                                'tesoreria_id': teso.id,
                                                'type': pagoC.type},
                                      context=context)
        return True

    def button_calculate(self, cr, uid, ids, context=None):
        facturas_emit = []
        facturas_rec = []
        estado = []
        pagoP_obj = self.pool['l10n.es.tesoreria.pagos.period']
        pagoV_obj = self.pool['l10n.es.tesoreria.pagos.var']
        pagoR_obj = self.pool['l10n.es.tesoreria.pagos.rece']
        pagoC_obj = self.pool['l10n.es.tesoreria.pagos.cash']
        t_factura_obj = self.pool['l10n.es.tesoreria.facturas']
        invoice_obj = self.pool['account.invoice']
        self.restart(cr, uid, ids, context=context)
        for teso in self.browse(cr, uid, ids, context=context):
            if teso.check_draft:
                estado.append("draft")
            if teso.check_proforma:
                estado.append("proforma")
            if teso.check_open:
                estado.append("open")
            invoices = invoice_obj.search(
                cr, uid, [('date_due', '>=', teso.inicio_validez),
                          ('date_due', '<=', teso.fin_validez),
                          ('state', 'in', tuple(estado))], context=context)
            for invoice in invoice_obj.browse(cr, uid, invoices,
                                              context=context):
                values = {}
                if invoice.type in ('in_invoice', 'out_invoice'):
                    values = {
                        'factura_id': invoice.id,
                        'fecha_vencimiento': invoice.date_due,
                        'partner_id': invoice.partner_id.id,
                        'diario': invoice.journal_id.id,
                        # 'tipo_pago': invoice.payment_type.id,
                        'payment_term': invoice.payment_term.id,
                        'estado': invoice.state,
                        'base': invoice.amount_untaxed,
                        'impuesto': invoice.amount_tax,
                        'total': invoice.amount_total,
                        'pendiente': invoice.residual,
                    }
                elif invoice.type in ('in_refund', 'out_refund'):
                    values = {
                        'factura_id': invoice.id,
                        'fecha_vencimiento': invoice.date_due,
                        'partner_id': invoice.partner_id.id,
                        'diario': invoice.journal_id.id,
                        # 'tipo_pago': invoice.payment_type.id,
                        'payment_term': invoice.payment_term.id,
                        'estado': invoice.state,
                        'base': -invoice.amount_untaxed,
                        'impuesto': -invoice.amount_tax,
                        'total': -invoice.amount_total,
                        'pendiente': -invoice.residual,
                    }
                id = t_factura_obj.create(cr, uid, values)
                if invoice.type == "out_invoice" or \
                        invoice.type == "out_refund":
                    facturas_emit.append(id)
                elif invoice.type == "in_invoice" or \
                        invoice.type == "in_refund":
                    facturas_rec.append(id)
            self.write(cr, uid, teso.id, {'facturas_emit':
                                          [(6, 0, facturas_emit)],
                                          'facturas_rec':
                                          [(6, 0, facturas_rec)]},
                       context=context)
            for pagoP in teso.plantilla.pagos_period:
                if ((pagoP.fecha >= teso.inicio_validez and
                        pagoP.fecha <= teso.fin_validez) or
                        not pagoP.fecha) and not pagoP.pagado:
                    values = {
                        'name': pagoP.name,
                        'fecha': pagoP.fecha,
                        'partner_id': pagoP.partner_id.id,
                        # 'payment_type': pagoP.payment_type.id,
                        'importe': pagoP.importe,
                        'tesoreria_id': teso.id,
                    }
                    pagoP_obj.create(cr, uid, values, context=context)
            for pagoV in teso.plantilla.pagos_var:
                if ((pagoV.fecha >= teso.inicio_validez and
                        pagoV.fecha <= teso.fin_validez) or not pagoV.fecha) \
                        and not pagoV.pagado:
                    values = {
                        'name': pagoV.name,
                        'fecha': pagoV.fecha,
                        'partner_id': pagoV.partner_id.id,
                        # 'payment_type': pagoV.payment_type.id,
                        'importe': pagoV.importe,
                        'tesoreria_id': teso.id,
                    }
                    pagoV_obj.create(cr, uid, values, context=context)
            for pagoR in teso.plantilla.pagos_rece:
                if (pagoR.fecha >= teso.inicio_validez and pagoR.fecha <=
                        teso.fin_validez)or not pagoR.fecha:
                    values = {
                        'name': pagoR.name,
                        'fecha': pagoR.fecha,
                        'diario': pagoR.diario.id,
                        # 'payment_type': pagoR.payment_type.id,
                        'importe': pagoR.importe,
                        'tesoreria_id': teso.id,
                    }
                    pagoR_obj.create(cr, uid, values, context=context)
            for pagoC in teso.plantilla.pagos_cash:
                if (pagoC.fecha >= teso.inicio_validez and pagoC.fecha <=
                        teso.fin_validez)or not pagoC.fecha:
                    values = {
                        'name': pagoC.name,
                        'fecha': pagoC.fecha,
                        'diario': pagoC.diario.id,
                        # 'payment_type': pagoC.payment_type.id,
                        'importe': pagoC.importe,
                        'type': pagoC.type,
                        'tesoreria_id': teso.id,
                    }
                    pagoC_obj.create(cr, uid, values, context=context)
        return True

    def restart(self, cr, uid, ids, context=None):

        res = super(L10nEsTesoreria, self).restart(cr, uid, ids,
                                                   context=context)

        pagoR_obj = self.pool['l10n.es.tesoreria.pagos.rece']
        pagoC_obj = self.pool['l10n.es.tesoreria.pagos.cash']

        for teso in self.browse(cr, uid, ids, context=context):
            for pagoR in teso.pagos_rece:
                pagoR_obj.unlink(cr, uid, pagoR.id, context=context)
            for pagoC in teso.pagos_cash:
                pagoC_obj.unlink(cr, uid, pagoC.id, context=context)
        return res

    def export_facturas_emitidas(self, cr, uid, ids, sheet2, context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet2.write(0, 0, 'FACTURAS EMITIDAS', boldS14)
        sheet2.write(3, 0, 'FECHA VENCIMIENTO', boldS)
        sheet2.write(3, 1, 'N. FACTURA', boldS)
        sheet2.write(3, 2, 'CLIENTE', boldS)
        sheet2.write(3, 3, 'DIARIO', boldS)
#        sheet2.write(3, 4, 'TIPO DE PAGO', boldS)
#        sheet2.write(3, 5, 'PLAZO DE PAGO', boldS)
#        sheet2.write(3, 6, 'BASE', boldS)
#        sheet2.write(3, 7, 'IMPUESTO', boldS)
#        sheet2.write(3, 8, 'TOTAL', boldS)
#        sheet2.write(3, 9, 'PENDIENTE', boldS)
#        sheet2.write(3, 10, 'ESTADO', boldS)
        sheet2.write(3, 4, 'PLAZO DE PAGO', boldS)
        sheet2.write(3, 5, 'BASE', boldS)
        sheet2.write(3, 6, 'IMPUESTO', boldS)
        sheet2.write(3, 7, 'TOTAL', boldS)
        sheet2.write(3, 8, 'PENDIENTE', boldS)
        sheet2.write(3, 9, 'ESTADO', boldS)
        lineKont = 5
        for line in tesoreria.facturas_emit:
            if line.factura_id:
                sheet2.write(lineKont, 0, line.fecha_vencimiento)
            if line.factura_id:
                sheet2.write(lineKont, 1, line.factura_id.number)
            if line.partner_id:
                sheet2.write(lineKont, 2, line.partner_id.name)
            if line.diario:
                sheet2.write(lineKont, 3, line.diario.name)
#            if line.tipo_pago:
#                sheet2.write(lineKont, 4, line.tipo_pago.name)
#            if line.payment_term:
#                sheet2.write(lineKont, 5, line.payment_term.name)
#            sheet2.write(lineKont, 6, str(line.base), numS)
#            sheet2.write(lineKont, 7, str(line.impuesto), numS)
#            sheet2.write(lineKont, 8, str(line.total), numS)
#            sheet2.write(lineKont, 9, str(line.pendiente), numS)
#            sheet2.write(lineKont, 10, line.estado)
            if line.payment_term:
                sheet2.write(lineKont, 4, line.payment_term.name)
            sheet2.write(lineKont, 5, str(line.base), numS)
            sheet2.write(lineKont, 6, str(line.impuesto), numS)
            sheet2.write(lineKont, 7, str(line.total), numS)
            sheet2.write(lineKont, 8, str(line.pendiente), numS)
            sheet2.write(lineKont, 9, line.estado)
            lineKont += 1
        return sheet2

    def export_facturas_recibidas(self, cr, uid, ids, sheet3,
                                  context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet3.write(0, 0, 'FACTURAS RECIBIDAS', boldS14)
        sheet3.write(3, 0, 'FECHA VENCIMIENTO', boldS)
        sheet3.write(3, 1, 'N. FACTURA', boldS)
        sheet3.write(3, 2, 'PROVEEDOR', boldS)
        sheet3.write(3, 3, 'DIARIO', boldS)
#        sheet3.write(3, 4, 'TIPO DE PAGO', boldS)
#        sheet3.write(3, 5, 'PLAZO DE PAGO', boldS)
#        sheet3.write(3, 6, 'BASE', boldS)
#        sheet3.write(3, 7, 'IMPUESTO', boldS)
#        sheet3.write(3, 8, 'TOTAL', boldS)
#        sheet3.write(3, 9, 'PENDIENTE', boldS)
#        sheet3.write(3, 10, 'ESTADO', boldS)
        sheet3.write(3, 4, 'PLAZO DE PAGO', boldS)
        sheet3.write(3, 5, 'BASE', boldS)
        sheet3.write(3, 6, 'IMPUESTO', boldS)
        sheet3.write(3, 7, 'TOTAL', boldS)
        sheet3.write(3, 8, 'PENDIENTE', boldS)
        sheet3.write(3, 9, 'ESTADO', boldS)
        lineKont = 5
        for line in tesoreria.facturas_rec:
            if line.factura_id:
                sheet3.write(lineKont, 0, line.fecha_vencimiento)
            if line.factura_id:
                sheet3.write(lineKont, 1, line.factura_id.number)
            if line.partner_id:
                sheet3.write(lineKont, 2, line.partner_id.name)
            if line.diario:
                sheet3.write(lineKont, 3, line.diario.name)
#            if line.tipo_pago:
#                sheet3.write(lineKont, 4, line.tipo_pago.name)
#            if line.payment_term:
#                sheet3.write(lineKont, 5, line.payment_term.name)
#            sheet3.write(lineKont, 6, str(line.base), numS)
#            sheet3.write(lineKont, 7, str(line.impuesto), numS)
#            sheet3.write(lineKont, 8, str(line.total), numS)
#            sheet3.write(lineKont, 9, str(line.pendiente), numS)
#            sheet3.write(lineKont, 10, line.estado)
            if line.payment_term:
                sheet3.write(lineKont, 4, line.payment_term.name)
            sheet3.write(lineKont, 5, str(line.base), numS)
            sheet3.write(lineKont, 6, str(line.impuesto), numS)
            sheet3.write(lineKont, 7, str(line.total), numS)
            sheet3.write(lineKont, 8, str(line.pendiente), numS)
            sheet3.write(lineKont, 9, line.estado)
            lineKont += 1
        return sheet3

    def export_pagos_periodicos(self, cr, uid, ids, sheet4, context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet4.write(0, 0, 'PAGOS PERIODICOS', boldS14)
        sheet4.write(3, 0, 'FECHA', boldS)
        sheet4.write(3, 1, 'DESCRIPCION', boldS)
        sheet4.write(3, 2, 'PROVEEDOR', boldS)
#        sheet4.write(3, 3, 'TIPO DE PAGO', boldS)
#        sheet4.write(3, 4, 'IMPORTE', boldS)
        sheet4.write(3, 3, 'IMPORTE', boldS)
        lineKont = 5
        for line in tesoreria.pagos_period:
            if line.fecha:
                sheet4.write(lineKont, 0, line.fecha)
            if line.name:
                sheet4.write(lineKont, 1, line.name)
            if line.partner_id:
                sheet4.write(lineKont, 2, line.partner_id.name)
#            if line.payment_type:
#                sheet4.write(lineKont, 3, line.payment_type.name)
#            sheet4.write(lineKont, 4, str(line.importe), numS)
            sheet4.write(lineKont, 3, str(line.importe), numS)
            lineKont += 1
        return sheet4

    def export_pagos_variables(self, cr, uid, ids, sheet5, context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet5.write(0, 0, 'PAGOS VARIABLES', boldS14)
        sheet5.write(3, 0, 'FECHA', boldS)
        sheet5.write(3, 1, 'DESCRIPCION', boldS)
        sheet5.write(3, 2, 'PROVEEDOR', boldS)
#        sheet5.write(3, 3, 'TIPO DE PAGO', boldS)
#        sheet5.write(3, 4, 'IMPORTE', boldS)
        sheet5.write(3, 3, 'IMPORTE', boldS)
        lineKont = 5
        for line in tesoreria.pagos_var:
            if line.fecha:
                sheet5.write(lineKont, 0, line.fecha)
            if line.name:
                sheet5.write(lineKont, 1, line.name)
            if line.partner_id:
                sheet5.write(lineKont, 2, line.partner_id.name)
#            if line.payment_type:
#                sheet5.write(lineKont, 3, line.payment_type.name)
#            sheet5.write(lineKont, 4, str(line.importe), numS)
            sheet5.write(lineKont, 3, str(line.importe), numS)
            lineKont += 1
        return sheet5

    def export_cobros_clientes(self, cr, uid, ids, sheet6, context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet6.write(0, 0, 'COBROS UNICOS', boldS14)
        sheet6.write(3, 0, 'FECHA', boldS)
        sheet6.write(3, 1, 'DESCRIPCION', boldS)
        sheet6.write(3, 2, 'DIARIO', boldS)
#        sheet6.write(3, 3, 'TIPO DE PAGO', boldS)
#        sheet6.write(3, 4, 'IMPORTE', boldS)
        sheet6.write(3, 3, 'IMPORTE', boldS)
        lineKont = 5
        for line in tesoreria.pagos_rece:
            if line.fecha:
                sheet6.write(lineKont, 0, line.fecha)
            if line.name:
                sheet6.write(lineKont, 1, line.name)
            if line.diario:
                sheet6.write(lineKont, 2, line.diario.name)
#            if line.payment_type:
#                sheet6.write(lineKont, 3, line.payment_type.name)
#            sheet6.write(lineKont, 4, str(line.importe), numS)
            sheet6.write(lineKont, 3, str(line.importe), numS)
            lineKont += 1
        return sheet6

    def export_cash_flow(self, cr, uid, ids, sheet7, context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet7.write(0, 0, 'CASH FLOW', boldS14)
        sheet7.write(3, 0, 'FECHA', boldS)
        sheet7.write(3, 1, 'DESCRIPCION', boldS)
        sheet7.write(3, 2, 'DIARIO', boldS)
#        sheet7.write(3, 3, 'TIPO DE PAGO', boldS)
#        sheet7.write(3, 4, 'TIPO', boldS)
#        sheet7.write(3, 5, 'IMPORTE', boldS)
        sheet7.write(3, 3, 'TIPO', boldS)
        sheet7.write(3, 4, 'IMPORTE', boldS)
        lineKont = 5
        for line in tesoreria.pagos_cash:
            if line.fecha:
                sheet7.write(lineKont, 0, line.fecha)
            if line.name:
                sheet7.write(lineKont, 1, line.name)
            if line.diario:
                sheet7.write(lineKont, 2, line.diario.name)
#            if line.payment_type:
#                sheet7.write(lineKont, 3, line.payment_type.name)
            type = 'Entrada'
            if line.type == 'out':
                type = 'Salida'
#            sheet7.write(lineKont, 4, type)
#            sheet7.write(lineKont, 5, str(line.importe), numS)
            sheet7.write(lineKont, 3, type)
            sheet7.write(lineKont, 4, str(line.importe), numS)
            lineKont += 1
        return sheet7

    def export_desglose_saldo(self, cr, uid, ids, sheet1, context=None):
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        sheet1.write(11, 0, 'DESGLOSE SALDO', boldS14)
        sheet1.write(14, 0, 'TIPO DE PAGO', boldS)
        sheet1.write(14, 1, 'MODO', boldS)
        sheet1.write(14, 2, 'IMPORTE', boldS)
        lineKont = 16
        for line in tesoreria.desglose_saldo:
            if line.name:
                sheet1.write(lineKont, 0, line.name)
            if line.type == 'in':
                sheet1.write(lineKont, 1, 'Entrada')
            elif line.type == 'out':
                sheet1.write(lineKont, 1, 'Salida')
            sheet1.write(lineKont, 2, str(line.saldo), numS)
            lineKont += 1
        return sheet1

    def export_csv(self, cr, uid, ids, context=None):
        adj_obj = self.pool['ir.attachment']
        tesoreria = self.browse(cr, uid, ids[0], context=context)
        fileDoc = xl.Workbook()
        boldFont16 = xl.Font()
        boldFont16.bold = True
        boldFont16.height = 260
        boldS16 = xl.XFStyle()
        boldS16.font = boldFont16
        boldFont14 = xl.Font()
        boldFont14.bold = True
        boldFont14.height = 220
        boldS14 = xl.XFStyle()
        boldS14.font = boldFont14
        boldFont = xl.Font()
        boldFont.bold = True
        boldS = xl.XFStyle()
        boldS.font = boldFont
        boldNS = xl.XFStyle()
        boldNS.font = boldFont
        boldNS.num_format_str = '#,##0.00'
        numS = xl.XFStyle()
        numS.num_format_str = '#,##0.00'
        sheet1 = fileDoc.add_sheet("Prevision Tesoreria")
        sheet1.write(1, 0, 'PREVISION TESORERIA', boldS16)
        sheet1.write(4, 0, 'Nombre:', boldS14)
        sheet1.write(4, 1, tesoreria.name, boldS14)
        sheet1.write(4, 3, 'SALDOS', boldS14)
        sheet1.write(6, 0, 'Fecha Inicio:', boldS)
        sheet1.write(6, 1, tesoreria.inicio_validez)
        sheet1.write(6, 3, 'Saldo Inicio:', boldS)
        sheet1.write(6, 4, str(tesoreria.saldo_inicial), numS)
        sheet1.write(7, 0, 'Fecha Final:', boldS)
        sheet1.write(7, 1, tesoreria.fin_validez)
        sheet1.write(7, 3, 'Saldo Final:', boldS)
        sheet1.write(7, 4, str(tesoreria.saldo_final), boldNS)
        if tesoreria.desglose_saldo:
            sheet1 = self.export_desglose_saldo(cr, uid, ids, sheet1,
                                                context=context)
        if tesoreria.facturas_emit:
            sheet2 = fileDoc.add_sheet("Facturas Emitidas")
            sheet2 = self.export_facturas_emitidas(cr, uid, ids, sheet2,
                                                   context=context)
        if tesoreria.facturas_rec:
            sheet3 = fileDoc.add_sheet("Facturas Recibidas")
            sheet3 = self.export_facturas_recibidas(cr, uid, ids, sheet3,
                                                    context=context)
        if tesoreria.pagos_period:
            sheet4 = fileDoc.add_sheet("Pagos Periodicos")
            sheet4 = self.export_pagos_periodicos(cr, uid, ids, sheet4,
                                                  context=context)
        if tesoreria.pagos_var:
            sheet5 = fileDoc.add_sheet("Pagos Variables")
            sheet5 = self.export_pagos_variables(cr, uid, ids, sheet5,
                                                 context=context)
        if tesoreria.pagos_rece:
            sheet6 = fileDoc.add_sheet("Cobros Unicos")
            sheet6 = self.export_cobros_clientes(cr, uid, ids, sheet6,
                                                 context=context)
        if tesoreria.pagos_cash:
            sheet7 = fileDoc.add_sheet("Cash-Flow")
            sheet7 = self.export_cash_flow(cr, uid, ids, sheet7,
                                           context=context)
        fname = 'Tesoreria_' + tesoreria.name + '.xls'
        file = StringIO.StringIO()
        fileDoc.save(file)
        fileDocFin = base64.encodestring(file.getvalue())
        res = {'csv_file': fileDocFin,
               'csv_fname': fname
               }
        wiz_id = self.pool.get('export.csv.wiz').create(cr, uid, res,
                                                        context=context)
        adj_list = adj_obj.search(cr, uid, [('res_id', '=', tesoreria.id),
                                            ('res_model', '=',
                                             'l10n.es.tesoreria')],
                                  context=context)
        kont = 1
        if adj_list:
            kont = len(adj_list) + 1
            adj_obj.create(cr, uid, {'name': ('Tesoreria ') + tesoreria.name +
                                     ' v.' + str(kont),
                                     'datas': fileDocFin,
                                     'datas_fname': fname,
                                     'res_model': 'l10n.es.tesoreria',
                                     'res_id': tesoreria.id,
                                     }, context=context)
        return {'type': 'ir.actions.act_window',
                'res_model': 'export.csv.wiz',
                'view_type': 'form',
                'view_mode': 'form',
                'nodestroy': True,
                'res_id': wiz_id,
                'target': 'new',
                }


class L10nEsTesoreriaSaldos(orm.Model):
    _inherit = 'l10n.es.tesoreria.saldos'
    _columns = {'type': fields.selection([('in', 'Entrada'),
                                          ('out', 'Salida')],
                                         'Tipo', required=True),
                }
#
#
# class L10nEsTesoreriaPagosPeriod(orm.Model):
#     _inherit = 'l10n.es.tesoreria.pagos.period'
#     _columns = {'payment_type': fields.many2one('payment.type',
#                                                 'Tipo de Pago'),
#                 }
#
#
# class L10nEsTesoreriaPagosVar(orm.Model):
#     _inherit = 'l10n.es.tesoreria.pagos.var'
#     _columns = {'payment_type': fields.many2one('payment.type',
#                                                 'Tipo de Pago'),
#                 }


class L10nEsTesoreriaPagosCash(orm.Model):
    _name = 'l10n.es.tesoreria.pagos.cash'

    def _get_entrada(self, cr, uid, ids, name, args, context=None):
        res = {}
        for cash in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            if cash.importe >= 0:
                amount = cash.importe
            res[cash.id] = amount
        return res

    def _get_salida(self, cr, uid, ids, name, args, context=None):
        res = {}
        for cash in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            if cash.importe <= 0:
                amount = cash.importe
            res[cash.id] = amount
        return res

    _columns = {'name': fields.char('Descripción', size=64),
                'fecha': fields.date('Fecha'),
                'diario': fields.many2one('account.journal', 'Diario',
                                          domain=[('type', '=', 'purchase')]),
                'importe': fields.float(
                    'Importe', digits_compute=dp.get_precision('Account')),
                # 'payment_type': fields.many2one('payment.type',
                #                                 'Tipo de Pago'),
                'type': fields.selection(
                    [('in', 'Entrada'), ('out', 'Salida')], 'Tipo',
                    required=True),
                'tesoreria_id': fields.many2one('l10n.es.tesoreria',
                                                'Plantilla Tesorería'),
                'entrada': fields.function(_get_entrada, method=True,
                                           type='float', string='Entrada',
                                           invisible=True),
                'salida': fields.function(_get_salida, method=True,
                                          type='float', string='Salida',
                                          invisible=True),
                }

    def _check_importe(self, cr, uid, ids, context=None):
        cash = self.browse(cr, uid, ids, context=context)
        res = True
        for flow in cash:
            if flow.type == 'in' and flow.importe <= 0.0:
                res = False
            if flow.type == 'out' and flow.importe >= 0.0:
                res = False
        return res

    _constraints = [
        (_check_importe, '\n\nCuidado con las líneas de Cash-Flow!\n Si es '
         'de tipo entrada, el importe debe ser positivo.\n Si es de tipo '
         'salida, el importe debe ser negativo.', ['type', 'importe']),
        ]


class L10nEsTesoreriaPagosRece(orm.Model):
    _name = 'l10n.es.tesoreria.pagos.rece'

    _columns = {'name': fields.char('Descripción', size=64),
                'fecha': fields.date('Fecha'),
                'diario': fields.many2one('account.journal', 'Diario',
                                          domain=[('type', '=', 'purchase')]),
                'importe': fields.float(
                    'Importe', digits_compute=dp.get_precision('Account')),
                # 'payment_type': fields.many2one('payment.type',
                #                                 'Tipo de Pago'),
                'tesoreria_id': fields.many2one('l10n.es.tesoreria',
                                                'Tesorería'),
                }
