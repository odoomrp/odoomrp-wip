# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, exceptions, _
from dateutil.relativedelta import relativedelta


class WizChangeProcurementDate(models.TransientModel):
    _inherit = 'wiz.change.procurement.date'

    def _take_procurements_to_treat(self, procurement_ids):
        procs = super(WizChangeProcurementDate,
                      self)._take_procurements_to_treat(procurement_ids)
        procs = procs.filtered(lambda x: x.level == 0)
        procs = procs.filtered(lambda x: not x.production_id or (
            x.production_id and x.production_id.state == 'draft'))
        return procs

    def _treat_procurements(self):
        super(WizChangeProcurementDate, self)._treat_procurements()
        route_id = self.env.ref('mrp.route_warehouse0_manufacture').id,
        procurements = self.procurements.filtered(
            lambda x: route_id[0] in x.product_id.route_ids.ids)
        self._treat_procurements_for_mo(procurements)

    def _modify_procurements_for_po(self, procurements):
        route_id = self.env.ref('mrp.route_warehouse0_manufacture').id,
        procurements = procurements.filtered(
            lambda x: route_id[0] not in x.product_id.route_ids.ids)
        super(WizChangeProcurementDate, self)._modify_procurements_for_po(
            procurements)

    def _treat_procurements_for_mo(self, procurements):
        for procurement in procurements:
            if procurement.date_planned > self.new_scheduled_date:
                timedelta = (fields.Datetime.from_string(
                    procurement.date_planned) - fields.Datetime.from_string(
                    self.new_scheduled_date)) * -1
            else:
                timedelta = fields.Datetime.from_string(
                    self.new_scheduled_date) - fields.Datetime.from_string(
                    procurement.date_planned)
            procurement.write({'date_planned': self.new_scheduled_date})
            if (procurement.production_id and
                    procurement.production_id.state == 'draft'):
                procurement.production_id.write(
                    {'date_planned': self.new_scheduled_date})
            if procurement.plan:
                self._treat_procurements_childrens(procurement, timedelta.days)

    def _treat_procurements_childrens(self, procurement, days_to_sum):
        route_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        proc_obj = self.env['procurement.order']
        cond = [('parent_procurement_id', 'child_of', procurement.id),
                ('id', '!=', procurement.id)]
        procs = proc_obj.search(cond)
        for proc in procs:
            new_date = (fields.Datetime.from_string(proc.date_planned) +
                        (relativedelta(days=days_to_sum)))
            proc.write({'date_planned': new_date})
            if route_id not in proc.product_id.route_ids.ids:
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
            else:
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
