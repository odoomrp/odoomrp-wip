# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta


class WizChangeProcurementDatePlanned(models.TransientModel):
    _name = 'wiz.change.procurement.date.planned'

    old_scheduled_date = fields.Datetime('Old scheduled date', readonly=True)
    new_scheduled_date = fields.Datetime('New scheduled date', required=True)

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
        if procu.date_planned > self.new_scheduled_date:
            days_to_sum = (fields.Datetime.from_string(
                procu.date_planned) - fields.Datetime.from_string(
                self.new_scheduled_date)) * -1
        else:
            days_to_sum = fields.Datetime.from_string(
                self.new_scheduled_date) - fields.Datetime.from_string(
                procu.date_planned)
        procu.write({'date_planned': self.new_scheduled_date})
        if procu.production_id and procu.production_id.state == 'draft':
            procu.production_id.write({'date_planned':
                                       self.new_scheduled_date})
        if (procu.purchase_line_id and procu.purchase_line_id.order_id.state !=
                'draft'):
            procu.purchase_line_id.write({'date_planned':
                                          self.new_scheduled_date})
        cond = [('parent_procurement_id', 'child_of', procu.id),
                ('id', '!=', procu.id)]
        procs = proc_obj.search(cond)
        for proc in procs:
            new_date = (fields.Datetime.from_string(proc.date_planned) +
                        (relativedelta(days=days_to_sum.days)))
            proc.write({'date_planned': new_date})
            if proc.purchase_line_id:
                if proc.purchase_line_id.order_id.state != 'draft':
                    raise exceptions.Warning(
                        _('You can not change the date planned of'
                          ' procurement order: %s, because the purchase'
                          ' order: %s, not in draft status') %
                        (proc.name, proc.purchase_line_id.order_id.name))
                else:
                    new_date = (fields.Datetime.from_string(
                                proc.purchase_line_id.date_planned) +
                                (relativedelta(days=days_to_sum)))
                    proc.purchase_line_id.write({'date_planned': new_date})
            if proc.production_id:
                if proc.production_id.state != 'draft':
                    raise exceptions.Warning(
                        _('You can not change the date planned of'
                          ' procurement order: %s, because the production'
                          ' order: %s, not in draft status') %
                        (proc.name, proc.production_id.name))
                else:
                    new_date = (fields.Datetime.from_string(
                                proc.production_id.date_planned) +
                                (relativedelta(days=days_to_sum)))
                    proc.production_id.write({'date_planned': new_date})
        res = {'view_type': 'form,tree',
               'res_model': 'procurement.plan',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_mode': 'form',
               'res_id': procu.plan.id,
               'target': 'current'
               }
        return res
