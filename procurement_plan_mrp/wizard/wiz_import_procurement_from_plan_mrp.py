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

from openerp import models, fields, api


class WizImportProcurementFromPlanMrp(models.TransientModel):

    _name = 'wiz.import.procurement.from.plan.mrp'

    procurements = fields.One2many(
        comodel_name='wiz.import.procurement.from.plan.mrp.line',
        inverse_name='wizard_id', string='Procurements')

    @api.model
    def default_get(self, var_fields):
        plan = self.env['procurement.plan'].browse(
            self.env.context['active_id'])
        cond = [('warehouse_id', '=', plan.warehouse_id.id),
                ('state', '!=', 'done'),
                ('plan', '=', False)]
        if plan.from_date:
            cond.append(('date_planned', '>=', plan.from_date))
        if plan.to_date:
            cond.append(('date_planned', '<=', plan.to_date))
        lines = []
        procurements = self.env['procurement.order'].search(cond)
        cond = [('name', '=', 'Manufacture')]
        route = self.env['stock.location.route'].search(cond)
        procs = procurements.filtered(
            lambda r: r.location_id.usage == 'internal'and route[0].id in
            r.product_id.route_ids.ids)
        for proc in procs:
            lines.append({'procurement_id': proc.id,
                          'name': proc.name,
                          'date_planned': proc.date_planned,
                          'location_id': proc.location_id.id,
                          'origin': proc.origin,
                          'product_id': proc.product_id.id,
                          'product_qty': proc.product_qty,
                          'product_uom': proc.product_uom.id,
                          'state': proc.state,
                          'rule_id': proc.rule_id.id or False,
                          'purchase_id': proc.purchase_id.id or False
                          })
        return {'procurements': lines}

    @api.one
    def select_all_mrp(self):
        self.procurements.write({'selected': True})

    @api.one
    def unselect_all_mrp(self):
        self.procurements.write({'selected': False})

    @api.one
    def import_procurements_mrp(self):
        self.ensure_one()
        proc_obj = self.env['procurement.order']
        proc_ids = [proc.procurement_id.id for proc
                    in self.procurements if proc.selected]
        cond = [('id', 'in', proc_ids)]
        proc_obj.search(cond).write({'plan': self.env.context['active_id']})
        return True


class WizImportProcurementFromPlanMrpLine(models.TransientModel):

    _name = 'wiz.import.procurement.from.plan.mrp.line'

    wizard_id = fields.Many2one(
        'wiz.import.procurement.from.plan.mrp', string="Wizard")
    selected = fields.Boolean(string='Select')
    procurement_id = fields.Many2one(
        'procurement.order', string='Procurement')
    name = fields.Text(string='Description')
    date_planned = fields.Datetime(string='Scheduled Date')
    location_id = fields.Many2one('stock.location',
                                  string='Procurement Location')
    origin = fields.Char(string='Source Document')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity')
    product_uom = fields.Many2one('product.uom',
                                  string='Product Unit of Measure')
    state = fields.Selection([
        ('cancel', 'Cancelled'),
        ('confirmed', 'Confirmed'),
        ('exception', 'Exception'),
        ('running', 'Running'),
        ('done', 'Done')], string='Status')
    rule_id = fields.Many2one('procurement.rule', string='Rule')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
