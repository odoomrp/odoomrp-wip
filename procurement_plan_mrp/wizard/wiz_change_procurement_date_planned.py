# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


class WizChangeProcurementDatePlanned(models.TransientModel):
    _name = 'wiz.change.procurement.date.planned'

    old_scheduled_date = fields.Datetime('Old scheduled date', readonly=True)
    days = fields.Integer(
        'Add or subtract days', required=True, help='Positive integer sum days'
        ', negative integer subtraction days')

    @api.model
    def default_get(self, var_fields):
        vals = {}
        proc = self.env['procurement.order'].browse(self._context['active_id'])
        if proc.location_type != 'internal':
            raise exceptions.Warning(
                _('Location of procurement order is not of type INTERNAL'))
        if proc.production_id and proc.production_id.state != 'draft':
            raise exceptions.Warning(
                _('Procurement order with production order in state: %s') %
                (proc.production_id.state))
        if (proc.purchase_line_id and proc.purchase_line_id.order_id.state !=
                'draft'):
            raise exceptions.Warning(
                _('Procurement order with purchase order in state: %s') %
                (proc.production_id.state))
        vals['old_scheduled_date'] = proc.date_planned
        return vals

    @api.multi
    def change_scheduled_date(self):
        proc_obj = self.env['procurement.order']
        procu = proc_obj.browse(self._context['active_id'])
        procu._change_date_planned_from_plan_for_mo(self.days)
        res = {'view_type': 'form,tree',
               'res_model': 'procurement.plan',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'res_id': procu.plan.id,
               'target': 'current'
               }
        return res
