# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _
from openerp.addons import decimal_precision as dp


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    analytic_account = fields.Many2one(
        'account.analytic.account', domain=[('type', '!=', 'view')],
        string='Analytic Account')

    @api.multi
    def create_repair_cost(self):
        analytic_line_obj = self.env['account.analytic.line']
        for record in self:
            if not record.analytic_account:
                continue
            lines = record.analytic_account.line_ids.filtered(
                lambda x: x.is_repair_cost and x.amount != 0)
            lines.unlink()
            for line in record.fees_lines.filtered('load_cost'):
                vals = record._catch_repair_line_information_for_analytic(line)
                if vals:
                    analytic_line_obj.create(vals)
            for line in record.operations.filtered(
                    lambda x: x.load_cost and x.type == 'add'):
                vals = record._catch_repair_line_information_for_analytic(line)
                if vals:
                    analytic_line_obj.create(vals)

    @api.model
    def action_repair_end(self):
        result = super(MrpRepair, self).action_repair_end()
        self.create_repair_cost()
        return result

    def _catch_repair_line_information_for_analytic(self, line):
        analytic_line_obj = self.env['account.analytic.line']
        journal = self.env.ref('mrp.analytic_journal_repair', False)
        if not journal:
            raise exceptions.Warning(_('Error!: Repair journal not found'))
        name = self.name
        if line.product_id.default_code:
            name += ' - ' + line.product_id.default_code
        categ_id = line.product_id.categ_id
        general_account = (line.product_id.property_account_income or
                           categ_id.property_account_income_categ or False)
        amount = line.cost_subtotal * -1
        if not amount:
            return False
        vals = {'name': name,
                'user_id': line.user_id.id,
                'date': analytic_line_obj._get_default_date(),
                'product_id': line.product_id.id,
                'unit_amount': line.product_uom_qty,
                'product_uom_id': line.product_uom.id,
                'amount': amount,
                'journal_id': journal.id,
                'account_id': self.analytic_account.id,
                'is_repair_cost': True,
                'general_account_id': general_account.id
                }
        return vals

    @api.multi
    def action_invoice_create(self, group=False):
        res = super(MrpRepair, self).action_invoice_create(group=group)
        for record in self.filtered('analytic_account'):
            record.mapped('fees_lines.invoice_line_id').write(
                {'account_analytic_id': record.analytic_account.id})
            record.mapped('operations.invoice_line_id').write(
                {'account_analytic_id': record.analytic_account.id})
        return res


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    @api.multi
    @api.depends('product_id', 'product_uom_qty', 'lot_id')
    def _compute_cost_subtotal(self):
        for line in self:
            std_price = 0
            if line.product_id.cost_method == 'real' and line.lot_id:
                quants = line.lot_id.quant_ids.filtered(
                    lambda x: x.location_id.usage == 'internal')
                if quants:
                    std_price = quants[:1].cost
            else:
                std_price = line.product_id.standard_price
            line.standard_price = std_price
            line.cost_subtotal = std_price * line.product_uom_qty

    standard_price = fields.Float(
        string='Cost Price', digits=dp.get_precision('Account'),
        compute='_compute_cost_subtotal', store=True)
    cost_subtotal = fields.Float(
        string='Cost Subtotal', digits=dp.get_precision('Account'),
        compute='_compute_cost_subtotal', store=True)
    user_id = fields.Many2one('res.users', string='User', required=True,
                              default=lambda self: self.env.user)
    load_cost = fields.Boolean(string='Load Cost', default=True)


class MrpRepairFee(models.Model):
    _inherit = 'mrp.repair.fee'

    @api.multi
    @api.depends('product_id', 'product_uom_qty')
    def _compute_cost_subtotal(self):
        for fee in self:
            fee.standard_price = fee.product_id.standard_price
            fee.cost_subtotal = (fee.product_id.standard_price *
                                 fee.product_uom_qty)

    user_id = fields.Many2one('res.users', string='User', required=True,
                              default=lambda self: self.env.user)
    load_cost = fields.Boolean(string='Load Cost', default=True)

    # Computed field and not related. Because only has to be reloaded when a
    # product or quantity is changed but not if products price is changed
    standard_price = fields.Float(
        string='Cost Price', digits=dp.get_precision('Account'),
        compute='_compute_cost_subtotal', store=True)
    cost_subtotal = fields.Float(
        string='Cost Subtotal', digits=dp.get_precision('Account'),
        compute='_compute_cost_subtotal', store=True)
