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
from openerp import models, fields, api, exceptions, _


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
            for line in record.operations.filtered('load_cost'):
                vals = record._catch_repair_line_information_for_analytic(line)
                if vals:
                    analytic_line_obj.create(vals)

    @api.one
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
        amount = line.product_id.standard_price * line.product_uom_qty * -1
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

    @api.one
    @api.model
    def action_invoice_create(self, group=False):
        res = super(MrpRepair, self).action_invoice_create(group=group)
        for line in self.fees_lines:
            if line.invoice_line_id and self.analytic_account:
                line.invoice_line_id.write({'account_analytic_id':
                                            self.analytic_account.id})
        for line in self.operations:
            if line.invoice_line_id and self.analytic_account:
                line.invoice_line_id.write({'account_analytic_id':
                                            self.analytic_account.id})
        return res


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'

    user_id = fields.Many2one('res.users', string='User', required=True,
                              default=lambda self: self.env.user)
    load_cost = fields.Boolean(string='Load Cost', default=True)


class MrpRepairFee(models.Model):
    _inherit = 'mrp.repair.fee'

    user_id = fields.Many2one('res.users', string='User', required=True,
                              default=lambda self: self.env.user)
    load_cost = fields.Boolean(string='Load Cost', default=True)
