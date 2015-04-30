# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    plan = fields.Many2one('procurement.plan', string='Plan')

    @api.model
    def _procure_orderpoint_confirm(self, use_new_cursor=False,
                                    company_id=False):
        my_cursor = False
        product_ids = []
        if 'procurement_ids' not in self.env.context:
            my_cursor = use_new_cursor
        else:
            products = [procurement.product_id for procurement in
                        self.env.context['procurement_ids']]
            for product in products:
                if product.id not in product_ids:
                    product_ids.append(product.id)
        result = super(ProcurementOrder, self)._procure_orderpoint_confirm(
            use_new_cursor=my_cursor, company_id=company_id)
        if (product_ids and self.env.context['active_model'] ==
                'procurement.plan'):
            cond = [('plan', '=', self.env.context['active_id']),
                    ('product_id', 'not in', product_ids)]
            orders = self.search(cond)
            for order in orders:
                order.plan = False
        return result

    @api.model
    def create(self, data):
        if 'plan' in self.env.context and 'plan' not in data:
            data.update({'plan': self.env.context.get('plan')})
        procurement = super(ProcurementOrder, self).create(data)
        return procurement

    @api.multi
    def button_remove_plan(self):
        template_obj = self.env['product.template']
        result = template_obj._get_act_window_dict(
            'procurements_plan.action_procurement_plan')
        result['domain'] = "[('id', '=', " + str(self.plan.id) + ")]"
        result['res_id'] = self.plan.id
        result['view_mode'] = 'form'
        result['views'] = []
        self.plan.write({'procurement_ids': [[3, self.id]]})
        return result
