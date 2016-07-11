# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


class WizChangeProcurementDate(models.TransientModel):
    _name = 'wiz.change.procurement.date'

    old_scheduled_date = fields.Datetime('Old scheduled date', readonly=True)
    days = fields.Integer(
        'Add or subtract days', required=True, help='Positive integer sum days'
        ', negative integer subtraction days')
    procurements = fields.Many2many(
        comodel_name='procurement.order', string='Procurements to treat',
        relation='rel_wiz_change_procurement_date',
        column1='wiz_change_procurement_date_id', column2='procurement_id',
        readonly=True)

    @api.model
    def default_get(self, var_fields):
        super(WizChangeProcurementDate, self).default_get(var_fields)
        vals = {}
        procurements = self._take_procurements_to_treat(
            self.env.context['active_ids'])
        if len(procurements) == 1:
            vals['old_scheduled_date'] = procurements[0].date_planned
        vals['procurements'] = [(6, 0, procurements.ids)]
        return vals

    def _take_procurements_to_treat(self, procurement_ids):
        procurements = self.env['procurement.order'].browse(procurement_ids)
        procurements = procurements.filtered(
            lambda x: x.location_type == 'internal')
        procurements = procurements.filtered(
            lambda x: not x.purchase_line_id or (
                x.purchase_line_id and x.purchase_line_id.order_id.state ==
                'draft'))
        return procurements

    @api.multi
    def change_scheduled_date(self):
        if not self.procurements:
            raise exceptions.Warning(
                _('Error!: No procurements found to treat.'))
        self.procurements._change_date_planned_from_plan_for_po(self.days)
