# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class WizChangeProcurementDate(models.TransientModel):
    _name = 'wiz.change.procurement.date'

    old_scheduled_date = fields.Datetime('Old scheduled date', readonly=True)
    new_scheduled_date = fields.Datetime('New scheduled date', required=True)
    procurements = fields.Many2many(
        comodel_name='procurement.order', string='Procurements to treat',
        relation='rel_wiz_change_procurement_date',
        column1='wiz_change_procurement_date_id', column2='procurement_id',
        readonly=True)

    @api.model
    def default_get(self, var_fields):
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
        self._treat_procurements()

    def _treat_procurements(self):
        self._modify_procurements_for_po(self.procurements)

    def _modify_procurements_for_po(self, procurements):
        procurements.write({'date_planned': self.new_scheduled_date})
        procurements = procurements.filtered(
            lambda x: x.purchase_line_id and
            x.purchase_line_id.order_id.state == 'draft')
        purchase_order_lines = self.env['purchase.order.line']
        purchase_order_lines |= procurements.mapped('purchase_line_id')
        purchase_order_lines.write({'date_planned': self.new_scheduled_date})
