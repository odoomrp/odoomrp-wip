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


class L10nEsTesoreriaPlantilla(orm.Model):
    _inherit = 'l10n.es.tesoreria.plantilla'

    _columns = {'pagos_rece': fields.one2many(
                'l10n.es.tesoreria.pagos.rece.plan', 'plan_tesoreria_id',
                'Cobros Unicos'),
                'pagos_cash': fields.one2many(
                'l10n.es.tesoreria.pagos.cash.plan', 'plan_tesoreria_id',
                'Cash-flow Financiero')
                }


class L10nEsTesoreriaPagosRecePlan(orm.Model):
    _name = 'l10n.es.tesoreria.pagos.rece.plan'

    _columns = {'name': fields.char('Descripción', size=64),
                'fecha': fields.date('Fecha'),
                'diario': fields.many2one('account.journal', 'Diario'),
                'importe': fields.float(
                    'Importe', digits_compute=dp.get_precision('Account')),
                # 'payment_type': fields.many2one('payment.type',
                #                                 'Tipo de Pago'),
                'plan_tesoreria_id': fields.many2one(
                    'l10n.es.tesoreria.plantilla', 'Plantilla Tesorería'),
                }


class L10nEsTesoreriaPagosCashPlan(orm.Model):
    _name = 'l10n.es.tesoreria.pagos.cash.plan'

    _columns = {'name': fields.char('Descripción', size=64),
                'fecha': fields.date('Fecha'),
                'diario': fields.many2one('account.journal', 'Diario'),
                'importe': fields.float(
                    'Importe', digits_compute=dp.get_precision('Account')),
                # 'payment_type': fields.many2one('payment.type',
                #                                 'Tipo de Pago'),
                'type': fields.selection([('in', 'Entrada'),
                                          ('out', 'Salida')],
                                         'Tipo', required=True),
                'plan_tesoreria_id': fields.many2one(
                    'l10n.es.tesoreria.plantilla', 'Plantilla Tesorería'),
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
        (_check_importe, '\n\nCuidado con las líneas de Cash-Flow!\n Si es de '
         'tipo entrada, el importe debe ser positivo.\n Si es de tipo salida, '
         'el importe debe ser negativo.', ['type', 'importe']),
        ]
#
#
# class L10nEsTesoreriaPagosVarPlan(orm.Model):
#     _inherit = 'l10n.es.tesoreria.pagos.var.plan'
#
#     _columns = {'payment_type': fields.many2one('payment.type',
#                                                 'Tipo de Pago'),
#                 }
#
#
# class L10nEsTesoreriaPagosPeriodPlan(orm.Model):
#     _inherit = 'l10n.es.tesoreria.pagos.period.plan'
#
#     _columns = {'payment_type': fields.many2one('payment.type',
#                                                 'Tipo de Pago'),
#                 }
