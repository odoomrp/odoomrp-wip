# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, exceptions, _


class WizSplitProduction(models.TransientModel):
    _name = 'wiz.split.production'
    _description = 'Wizard split production'

    product_qty = fields.Integer('Quantity to produce', readonly=True)
    capacity_min = fields.Integer('Capacity min.', readonly=True)
    capacity_max = fields.Integer('Capacity min.', readonly=True)
    lines = fields.One2many(
        comodel_name='wiz.split.production.line',
        inverse_name='wizard', string='Lines')

    @api.model
    def default_get(self, var_fields):
        production = self.env['mrp.production'].browse(
            self.env.context['active_id'])
        lines = []
        pending = production.product_qty
        while pending > 0:
            if pending > production.capacity_max:
                lines.append((0, 0, {'quantity': production.capacity_max}))
                pending -= production.capacity_max
            else:
                lines.append((0, 0, {'quantity': pending}))
                pending = 0
        return {'product_qty': production.product_qty,
                'capacity_min': production.capacity_min,
                'capacity_max': production.capacity_max,
                'lines': lines}

    @api.multi
    def split_quantity(self):
        model_obj = self.env['ir.model.data']
        productions = []
        production = self.env['mrp.production'].browse(
            self.env.context['active_id'])
        first = True
        for line in self.lines:
            if self.capacity_min and line.quantity < self.capacity_min:
                raise exceptions.Warning(
                    _('Quantity < Capacity per cycle minimum'))
            if self.capacity_max and line.quantity > self.capacity_max:
                raise exceptions.Warning(
                    _('Quantity > Capacity per cycle maximum'))
            vals = {'product_qty': line.quantity,
                    'capacity_min': 0,
                    'capacity_max': 0}
            if first:
                first = False
                production.write(vals)
                productions.append(production.id)
            else:
                new_production = production.copy(vals)
                productions.append(new_production.id)
        t = model_obj.get_object_reference('mrp', 'mrp_production_tree_view')
        f = model_obj.get_object_reference('mrp', 'mrp_production_form_view')
        s = model_obj.get_object_reference('mrp', 'view_mrp_production_filter')
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,graph,gantt',
            'view_type': 'form',
            'res_model': 'mrp.production',
            'views': [(t and t[1] or False, 'tree'),
                      (f and f[1] or False, 'form')],
            'search_view_id': s and s[1] or False,
            'domain':
            "[('id','in',[" + ','.join(map(str, productions)) + "])]",
            'context': self.env.context,
            'target': 'current',
            }


class WizSplitProductionLine(models.TransientModel):
    _name = 'wiz.split.production.line'

    wizard = fields.Many2one(
        comodel_name='wiz.split.production', string='Wizard lines')
    quantity = fields.Integer('Quantity', required=True)
